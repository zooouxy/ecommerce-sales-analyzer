# Phase 5 — Structured Data + RAG Hybrid

## 阶段概述

Phase 5 将 AI Ecommerce Analyst 从“结构化数据 Tool 调度”扩展为“结构化事实 + RAG 业务知识”的混合架构。

原有结构化数据访问链路保持不变：

```text
用户
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

核心业务事实继续由 Pandas、Python、SQL 和 Query Service 确定性提供；RAG 负责业务定义、解释框架、客户运营策略、商品分析方法、趋势解释和业务建议。

LLM 仍然不直接查询 SQLite。

## Phase 5 目标

本阶段围绕三种路由模式设计：

```text
Structured-only
→ 结构化分析 Tool
→ 确定性业务事实

RAG-only
→ business_knowledge_search
→ 检索业务知识

Hybrid
→ 结构化分析 Tool
+ business_knowledge_search
→ 事实 + 业务知识组合回答
```

核心职责分离：

```text
SQL / Query Service
→ 回答“事实和数字是什么”

RAG
→ 回答“应该如何理解和行动”

LLM / Agent
→ 判断应该调用什么来源，并组织证据
```

## 知识库

本地知识库包含 5 个中英双语 Markdown 文档：

```text
knowledge/customer_segment_playbook.md
knowledge/sales_trend_interpretation.md
knowledge/product_performance_playbook.md
knowledge/ecommerce_kpi_definitions.md
knowledge/business_recommendation_rules.md
```

每个文档包含用于约束用途的 Metadata：

```text
domain
use_for
do_not_use_for
structured_source_for_facts
```

知识库不会取代 SQL，也不新增未经结构化数据验证的业务数字事实。

## Knowledge Loader 与 Chunking

`src/rag/knowledge_loader.py` 使用纯 Python 实现 Markdown 加载与按标题切分。

当前规则：

- 按 Markdown Heading 切分
- Metadata 不进入检索正文
- 中文和英文内容均保留
- 文档一级标题与语言标题不作为业务 Chunk
- 不引入 LangChain / LlamaIndex

当前知识库生成 84 个 Chunk。

## Embedding 与本地向量存储

`src/rag/embedding_provider.py` 接入 SiliconFlow Embeddings。

当前模型：

```text
Qwen/Qwen3-Embedding-0.6B
```

`src/rag/vector_store.py` 使用：

```text
NumPy cosine similarity
JSON 本地持久化
data/rag_index.json
```

当前 Embedding 维度为 1024。

项目不依赖 FAISS、Chroma 或外部 Vector Database。

## Retriever

`src/rag/retriever.py` 实现 `KnowledgeRetriever`。

当前能力：

- 语言偏好
- 中英重复内容抑制
- 低价值 Section 过滤
- 先扩大候选集，再选最终 top-k
- 不对另一语言做硬过滤

`top_k` 表示最终保留的检索 Chunk 数量，用于控制检索广度，而不是控制最终回答必须有多少条建议。

## RAG Tool 集成

Agent 通过：

```text
business_knowledge_search
```

访问业务知识。

该 Tool 继续遵循现有：

```text
Tool Registry
→ Tool Router
→ Agent
```

架构。

适用内容包括：

- 业务定义
- KPI 含义
- 客户分群策略
- 商品表现解释
- 趋势解释
- 业务建议框架

它不负责提供确定性的交易数据事实。

## Provenance-Constrained Knowledge Output

Phase 5 的一个核心可靠性改进，是对支持的客户分群知识采用确定性输出链路。

当前链路：

```text
Retriever
→ Knowledge Claims
→ Knowledge Selector
→ Knowledge Renderer
```

对应模块：

```text
src/rag/knowledge_claims.py
src/rag/knowledge_selector.py
src/rag/knowledge_renderer.py
```

客户分群知识会被解析为结构化 Claims，例如：

```text
characteristics
recommended_actions
```

当用户明确询问 Champions 等具体分群时，Selector 只保留对应分群的 Claim。

最终由 Renderer 直接生成知识回答，避免 LLM 自行添加知识库中不存在的具体措施。

## Deterministic RAG

对于支持的纯 RAG 问题，Agent 返回：

```text
answer_mode = deterministic_rag
```

例如：

```text
Champions客户应该怎么运营？
```

最终答案直接来自被选择并渲染的 Knowledge Claim。

这样可以避免 LLM 将“会员权益或优先体验”进一步自由扩展成 VIP 通道、专属折扣、邀请返利等知识库中没有明确提供的内容。

## Deterministic Hybrid

对于支持的客户分群 Hybrid 问题，Agent 返回：

```text
answer_mode = deterministic_hybrid
```

例如：

```text
Champions客户贡献了多少收入，并且应该怎么运营？
```

回答由两部分确定性组合：

```text
customer_segments
→ 结构化客户分群事实

business_knowledge_search
→ 确定性知识渲染

Agent
→ 确定性组合
```

因此最终答案不会让 LLM 再次改写结构化数字或扩写知识库建议。

## 模型通用知识

系统允许用户显式请求知识库之外的通用电商建议。

例如：

```text
除了知识库里的策略，还有哪些通用运营建议？
```

此时 Agent 可以使用模型通用知识，但最终回答会被确定性标记为：

```text
通用建议（非知识库内容）

以下建议来自模型通用电商知识，
不属于当前知识库检索内容。
```

这样可以避免模型通用知识被误认为来自 RAG 知识库。

## Grounding Validator

Phase 5 扩展了轻量、确定性的 Grounding Validator。

当前检查包括：

- Tool 是否执行成功
- 回答是否包含无直接证据支持的数字
- 回答是否自行添加未经支持的币种或货币单位
- 结构化数字证据
- 是否调用 RAG Tool
- RAG 是否返回可用证据
- 检索来源追踪

RAG 相似度 Score 等数值元数据不会被当成结构化业务数字证据。

Grounding Validator 仍然不是第二个语义推理模型。

## Deterministic Sanitizer

对于自由 LLM 生成的回答，如果出现未经证据支持的具体数字或币种，可以通过确定性 Sanitizer 删除相关内容。

当前只处理：

```text
unsupported_numbers
unsupported_currency
```

Sanitizer 不重新进行语义生成，也不会用新的数字替代原内容。

## Source Alignment

当 Knowledge Selector 已经生成最终使用的 `sources` 时，Grounding 会优先使用该来源列表进行展示。

如果没有最终 `sources`，则回退到原始 Retrieval `results`，保持对其他 RAG 场景的兼容。

这样可以保持：

```text
最终回答
↔ 实际使用知识
↔ Trace 展示来源
```

一致。

## Streamlit 集成

AI Analyst Trace 当前会展示：

```text
Answer Mode
Tool Calls
Tool Results
Grounding Validation
Knowledge Sources
```

只有存在检索来源时才显示 `Knowledge Sources`。

典型 Answer Mode：

```text
deterministic_rag
deterministic_hybrid
LLM synthesis with grounded tool evidence
```

## 回归测试

Phase 5 新增：

```text
tests/test_phase5_regression.py
```

覆盖场景：

```text
Structured-only
RAG-only
Hybrid
General Suggestions
Phase 4 商品比较回归
```

已验证：

```text
ALL PHASE 5 AGENT REGRESSION TESTS PASSED
```

Streamlit 中的主要 Phase 5 路由场景也已完成 UI 验收。

## 环境变量

Phase 5 需要：

```text
SILICONFLOW_API_KEY=your_api_key
SILICONFLOW_MODEL=Qwen/Qwen3-8B
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
```

`.env` 不应提交到 Git。

## 已知限制

Phase 5 有意保持“最小、清晰、可演示”，而不是扩展为大型 RAG 平台。

当前限制包括：

- 确定性 Knowledge Claim 抽取目前主要覆盖客户分群知识
- 其他知识域仍可能使用检索 Chunk + LLM 生成
- Grounding Validation 不执行完整语义蕴含或矛盾判断
- LLM 即使使用了有证据的数字，也仍可能在自由文本中描述错误的高低关系
- 知识库目前为本地维护
- 当前没有 reranker、BM25、query rewriting、外部向量数据库或第二个 LLM Judge
- `temperature=0` 只能降低波动，不代表完全确定
- 模型通用知识只有在用户明确请求时才允许使用，并且必须与知识库内容明确区分

这些限制属于作品集规模项目的主动 Scope Control。

## Phase 5 结果

Phase 5 已完成。

项目当前已经能够展示：

```text
确定性结构化分析
+
本地语义检索
+
来源可追踪的 RAG
+
确定性知识渲染
+
Structured + RAG Hybrid
+
模型通用知识来源分层
+
轻量 Grounding
+
Streamlit 可观察 Agent Trace
```
