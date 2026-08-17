# TODO

## Completed (v0.1 & v0.2)
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
- [x] Add unit test suite (36/36 tests passing).
- [x] Create `main.py` demonstration script.

## Next Milestone (v0.3 - Planned)
- [ ] Implement `Planner` service & task decomposition engine.
- [ ] Support multi-step task workflow execution.

## Future Milestones
- [ ] Milestone v0.4: Advanced Capability & Performance Scheduler.
- [ ] Milestone v0.5: Evaluator service & PerformanceTracker adaptive feedback loop.
- [ ] Milestone v0.6: Recovery system & Persistent Memory integration.
- [ ] Milestone v0.7: LangGraph orchestration integration.
- [ ] Infrastructure: FastAPI, LiteLLM, PostgreSQL, Redis, Celery.
