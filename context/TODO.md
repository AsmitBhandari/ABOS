# TODO

## Completed (v0.1, v0.2, v0.3, v0.4 & v0.5 Pre-Release)
- [x] Create persistent context directory (`context/`).
- [x] Implemented initial core abstractions (`Task`, `Agent`, `Tool`, `Result`).
- [x] Implemented `CalculatorAgent` with AST node evaluation.
- [x] Implemented `Orchestrator` for capability-based routing.
- [x] Establish seven canonical core domain contracts (`Task`, `BaseAgent`, `BaseTool`, `Result`, `Execution`, `Evaluation`, `AgentProfile`).
- [x] Support hierarchical parent/child tasks in `Task` contract.
- [x] Separate `Result` execution output from `Evaluation` quality assessment.
- [x] Implement `Execution` attempt tracking and status.
- [x] Implement `AgentProfile` quantitative historical performance tracking.
- [x] Add mandatory Core Domain Independence Rule to `context/RULES.md`.
- [x] Implement `Planner` abstract contract (`orchestration/planner/base.py`).
- [x] Implement `PlanningResult` structured container.
- [x] Implement `DeterministicPlanner` rule-based decomposition engine.
- [x] Implement `DecompositionValidator` for hierarchy and isolation integrity.
- [x] Implement `Scheduler` abstract contract (`orchestration/scheduler/base.py`).
- [x] Implement `SchedulingResult` and `CandidateScore` structured containers.
- [x] Implement `ScoringPolicy` with configurable weights and latency normalization.
- [x] Implement `DeterministicScheduler` with capability/state filtering and deterministic tie-breaking.
- [x] Implement safe fallback handling for agents missing `AgentProfile`.
- [x] Verify domain object immutability during scheduling.
- [x] Implement `PerformanceTracker` in `orchestration/performance/tracker.py`.
- [x] Implement cumulative success rate calculation.
- [x] Implement incremental cumulative average latency calculation.
- [x] Implement evidence-based confidence score progression.
- [x] Implement execution quality and correctness score aggregation.
- [x] Implement in-memory evaluation idempotency tracking.
- [x] Establish closed-loop adaptive feedback: `Execution -> Result -> Evaluation -> PerformanceTracker -> AgentProfile -> Scheduler`.
- [x] Implement `TextAnalysisAgent` (`agents/text_analysis_agent.py`) with word counting.
- [x] Implement `UnitConversionAgent` (`agents/unit_conversion_agent.py`) with length conversions.
- [x] Verify multi-agent capability-based routing and execution across all three specialized agents.
- [x] Verify performance-aware multi-agent routing between same-capability agents.
- [x] Expand comprehensive unit test suite (116/116 tests passing).
- [x] Verify runtime demonstration (`main.py`).

## Next Milestone (v0.6 - Planned)
- [ ] Implement `Recovery` subsystem & failure handling strategies.
- [ ] Implement retry policies and alternate agent selection on failure.
- [ ] Implement failure classification and task reassignment.

## Future Milestones
- [ ] Milestone v0.7: Persistent Memory integration.
- [ ] Milestone v0.8: LangGraph orchestration integration.
- [ ] Milestone v0.9: LLM Planner integration.
- [ ] Infrastructure: FastAPI, LiteLLM, PostgreSQL, Redis, Celery.
