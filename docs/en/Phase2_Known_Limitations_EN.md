Phase 2 — LLM Agent Integration & Fact-Grounded Tool Orchestration
Known Limitations
This document records confirmed limitations of the current Phase 2 implementation that are not considered blockers for phase acceptance. They mainly originate from probabilistic LLM behavior, temporal ambiguity in a static historical dataset, and the intentionally limited scope of the Grounding Validator.
1. Relative-Time Interpretation
The project currently operates on a static historical ecommerce dataset rather than a real-time business database. Relative-time expressions such as “last month,” “same period last year,” or “the most recent month” therefore do not have a unique reference point.
For example, “How were sales last month?” cannot inherently determine whether “last month” refers to the current real-world date, the latest month in the dataset, or another business period intended by the user.
Current strategy:
Explicit year and month → query monthly_sales normally
Month provided without a year → ask the user to provide the year
Ambiguous relative time → prefer clarification before querying
Relative-time clarification is mainly guided through the System Prompt and therefore cannot be guaranteed for every possible natural-language variation. The current version intentionally does not implement a complete natural-language temporal parser or an exhaustive list of relative-time keywords and regular expressions. This is an explicit system boundary.
2. Numeric Semantics in the Grounding Validator
The current Grounding Validator is a deterministic consistency checker rather than a complete natural-language factual verification system. Its main responsibilities are:
Checking Tool execution success
Checking whether important numeric values are supported by current evidence
Detecting unsupported currency information
Grounding evidence currently includes:
Tool Call Arguments + Tool Results
This allows query entity identifiers such as customer_id = 999999 and stock_code = ZZZ999 to appear legitimately in the final answer even when the Tool returns an empty result.
However, some numeric business labels can still produce minor false positives. For example, the number 10 in “Top 10” is part of a metric label rather than a newly generated business value, but the current Validator may still classify it as unsupported_numbers. This does not affect the correctness of the underlying Query Service, SQL logic, or business data, so Phase 2 does not add a more complex semantic grounding system for this edge case.
3. Unrequested Derived Metrics
The Agent may perform simple and logically valid mathematical derivations when explicitly requested by the user.
For example, if the user asks what percentage of November 2011 revenue came from product 22423, the Agent may calculate product revenue divided by monthly revenue using Tool Results.
However, the current LLM may occasionally generate an additional derived metric even when the user did not explicitly request it. The System Prompt instructs the model to derive new metrics only when explicitly needed and to avoid adding unrequested metrics. Because LLM generation is probabilistic, this behavior cannot be eliminated completely through prompt instructions alone. The current version records this as a model-generation limitation rather than introducing a mathematical proof engine or full claim-validation architecture.
4. Currency Metadata
The current Query Service and Tool Results do not expose an explicit currency field. Therefore, the system has no factual basis for assuming that revenue values are denominated in CNY, USD, EUR, GBP, or another currency.
The Agent must not automatically append labels such as yuan, RMB, CNY, USD, or EUR. Revenue is currently presented as a numeric value only.
The Grounding Validator flags unsupported currency assumptions as unsupported_currency.
5. Probabilistic LLM Behavior
The current Agent relies on an LLM for intent understanding, Tool selection, parameter extraction, multi-Tool planning, and final natural-language generation. As a result, identical user questions may occasionally produce small behavioral differences across requests.
Phase 2 reduces instability on core paths through Intent Matrix tests, Edge Case tests, Empty Result tests, Multi-tool tests, and Acceptance tests, but does not claim fully deterministic behavior for every possible natural-language input.
Core business calculations remain deterministic because they are handled by SQL, Query Service, and Python business logic rather than the LLM.
6. Grounding Validator Scope
The Grounding Validator is intentionally limited to deterministic consistency checks. It does not attempt to fully determine whether:
Comparative claims are semantically justified
Ranking claims are correct
Trend language is appropriate
Business classifications are valid
Complex mathematical derivations are logically proven
All natural-language interpretations are semantically correct
Important deterministic business judgments should preferably be exposed by backend business rules, SQL models, Query Service functions, or Tool Results. For example, if the system later needs to determine whether a product is in the Top 10, the preferred backend design would expose rank or is_top_10 rather than asking the LLM to infer ranking from aggregate metrics.
Phase 2 Acceptance Scope
Phase 2 — LLM Agent Integration & Fact-Grounded Tool Orchestration currently covers:
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
The known limitations documented above are not considered blockers for Phase 2 completion. More advanced capabilities such as Structured Claims, generic Parameter Grounding, comprehensive temporal parsing, and advanced multi-step reasoning may be considered in later phases only if real project requirements justify them.