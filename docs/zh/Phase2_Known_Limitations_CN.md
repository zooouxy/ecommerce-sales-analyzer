Phase 2 — LLM 智能体集成与基于事实的工具调度
Known Limitations / 已知限制
本文记录 Phase 2 当前版本中已经确认、但不作为阶段验收阻塞项的系统限制。这些限制主要来自自然语言模型的概率性行为、静态历史数据的时间语义边界，以及当前 Grounding Validator 的有限职责。
1. 相对时间解释
本项目当前使用静态历史电商数据，而不是实时业务数据库。因此，“上个月”“去年同期”“最近一个月”等相对时间表达缺少唯一的时间参考点。
例如，“上个月销售怎么样？”无法天然确定“上个月”是相对于现实世界当前月份、数据集最新月份，还是用户心中的某个业务时间点。
当前策略：
明确年月 → 正常调用 monthly_sales
缺少年份但明确月份 → 请求用户补充年份
相对时间且参考点不明确 → Agent 应优先请求用户澄清
相对时间澄清主要通过 System Prompt 引导 LLM，因此不能保证所有自然语言表达都能 100% 稳定触发澄清。当前版本不实现完整的自然语言时间解析器，也不通过大量关键词或正则表达式穷举所有相对时间表达。这是有意保留的系统边界。
2. Grounding Validator 的数字语义边界
当前 Grounding Validator 是一个确定性一致性检查器，而不是完整的自然语言事实验证系统。它主要检查：
Tool 是否成功执行
回答中的关键数字是否有当前证据支持
回答是否添加了没有证据支持的币种
Grounding evidence 当前主要来自：
Tool Call Arguments + Tool Results
这使得 customer_id = 999999、stock_code = ZZZ999 等查询实体参数，即使 Tool 返回空结果，也可以作为合法的实体身份信息出现在最终回答中。
但是部分带数字的业务标签仍可能产生轻微 false positive。例如 “Top 10” 中的数字 10 属于指标名称的一部分，而不是新生成的业务数值，当前 Validator 仍可能将其识别为 unsupported_numbers。该问题不会影响 Query Service、SQL 或底层业务数据的正确性，因此当前阶段不继续扩展复杂的语义 Grounding 系统。
3. LLM 可能生成用户未明确要求的派生指标
Agent 允许在用户明确需要时，根据 Tool Result 进行简单、直接且逻辑成立的数学推导。
例如用户明确询问“商品22423的收入占2011年11月销售收入多少？”，Agent 可以基于商品收入 ÷ 当月销售收入计算比例。
但当前 LLM 仍可能偶尔主动生成用户没有明确要求的派生指标。System Prompt 已要求仅在用户明确需要时进行数学推导，并避免补充用户未询问的额外指标；由于 LLM 具有概率性，该行为不能保证完全消失。当前将其记录为模型生成限制，不建设额外的数学证明或 Claim Validation 系统。
4. 币种信息
当前 Query Service 和 Tool Result 没有提供明确的 currency 字段，因此系统没有事实依据判断收入数据属于人民币、美元、欧元、英镑或其他货币。
Agent 当前不得自动为收入添加“元”“人民币”“CNY”“USD”“EUR”等货币单位。金额在当前阶段仅作为数值展示。
Grounding Validator 会将没有 Tool Result 支持的币种标记为 unsupported_currency。
5. LLM 行为具有概率性
当前 Agent 使用 LLM 完成用户意图理解、Tool 选择、参数提取、多 Tool 规划和最终自然语言生成，因此相同问题在不同请求中可能出现轻微行为差异。
Phase 2 已通过 Intent Matrix、Edge Case Tests、Empty Result Tests、Multi-tool Tests 和 Acceptance Test 降低核心路径的不稳定性，但不会宣称所有自然语言输入都具有完全确定的行为。
核心业务计算仍由 SQL、Query Service 和 Python Business Logic 负责，以保证核心业务事实的确定性。
6. Grounding Validator 的职责边界
Grounding Validator 当前只负责确定性、一致性层面的检查。它不负责完整判断：
比较结论是否合理
排名是否正确
趋势语言是否准确
业务分类是否成立
复杂数学推导是否合法
自然语言解释是否完全符合业务语义
重要的确定性业务判断应优先由后端业务规则、SQL、Query Service 或 Tool Result 提供。例如未来如果需要判断某商品是否属于 Top 10，更合适的方式是后端直接提供 rank 或 is_top_10，而不是要求 LLM 根据聚合指标自行推断。
Phase 2 验收范围
Phase 2 — LLM 智能体集成与基于事实的工具调度，当前验收覆盖：
LLM Provider Abstraction
SiliconFlow Provider
Tool Calling
Agent Multi-round Loop
Tool Router
Query Service Integration
6 Core Tool Intent Routing
Parameter Extraction
Empty Result Handling
Grounding Validation
Multi-tool Orchestration
Duplicate Tool Call Control
Deterministic Edge Cases
Phase 2 Acceptance Test
以上已知限制不会阻塞 Phase 2 完成。更复杂的 Structured Claims、通用 Parameter Grounding、完整时间解析和高级多步推理，可在后续阶段根据真实需求决定是否实现。