# TODO

## Completed (v0.1, v0.2 & v0.3)
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
- [x] Add comprehensive unit test suite (53/53 tests passing).
- [x] Verify runtime demonstration (`main.py`).

## Next Milestone (v0.4 - Planned)
- [ ] Implement `Scheduler` abstraction and capability matching engine.
- [ ] Incorporate `AgentProfile` performance scoring into agent selection.
- [ ] Support configurable scheduler weights and agent availability consideration.

## Future Milestones
- [ ] Milestone v0.5: Evaluator service & PerformanceTracker adaptive feedback loop.
- [ ] Milestone v0.6: Recovery system & Persistent Memory integration.
- [ ] Milestone v0.7: LangGraph orchestration integration.
- [ ] Milestone v0.8: LLM Planner integration.
- [ ] Infrastructure: FastAPI, LiteLLM, PostgreSQL, Redis, Celery.
