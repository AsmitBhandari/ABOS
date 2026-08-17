# Architectural Decisions Log

## Decision 1: Agent must remain LLM-independent

**Date**: 2026-08-16

**Decision**:
The base `Agent` abstraction must not depend directly on an LLM provider or external framework.

**Reason**:
ABOS must support deterministic agents, ML agents, rule-based agents, and LLM agents under a unified interface.

**Alternatives Considered**:
- Use LangChain/CrewAI base classes.
- Assume all agents take natural language prompts and return text via LLM APIs.

**Consequences**:
The `BaseAgent` interface remains generic, lightweight, and framework-independent.

---

## Decision 2: Safe AST parsing for mathematical evaluation

**Date**: 2026-08-16

**Decision**:
`CalculatorAgent` must parse and evaluate arithmetic expressions using standard Python AST node traversal rather than `eval()`.

**Reason**:
Passing raw strings to `eval()` allows arbitrary code execution (e.g. `__import__('os').system(...)`), creating a severe security vulnerability.

**Alternatives Considered**:
- Direct `eval()`.
- External math parsing libraries (`sympy`, `numexpr`).

**Consequences**:
Maintains strict security without adding external dependencies.

---

## Decision 3: Standardized Result object across all execution flows

**Date**: 2026-08-16

**Decision**:
Every agent execution must return a `Result` dataclass containing `success`, `output`, `error`, `agent_id`, `execution_id`, and `metadata`.

**Reason**:
Guarantees consistent error handling and outcome reporting throughout the orchestrator and caller pipeline without unstructured runtime exceptions.

**Alternatives Considered**:
- Throwing exceptions directly to the orchestrator.
- Returning raw values or tuples.

**Consequences**:
Execution failures are captured safely in a structured, serializable format.

---

## Decision 4: Core domain contracts are framework-independent

**Date**: 2026-08-17

**Decision**:
All seven core domain contracts (`Task`, `Agent`, `Tool`, `Result`, `Execution`, `Evaluation`, `AgentProfile`) must remain pure Python dataclasses/classes without dependencies on external frameworks (FastAPI, Pydantic, LangChain, LangGraph, LiteLLM, SQLAlchemy, Redis, Celery).

**Reason**:
Keeps the ABOS domain model clean, portable, lightweight, and adaptable to any runtime or framework.

**Consequences**:
Core objects contain only domain logic and lightweight validation. Infrastructure logic is strictly deferred to adapters and services.

---

## Decision 5: Task supports hierarchical parent/child relationships

**Date**: 2026-08-17

**Decision**:
`Task` includes `parent_task_id` and `child_task_ids` fields to represent task hierarchies.

**Reason**:
Enables representation of composite tasks resulting from task decomposition without embedding planning or decomposition logic inside the `Task` object itself.

**Consequences**:
Future `Planner` components can decompose high-level tasks into subtasks while sharing the standard `Task` data contract.

---

## Decision 6: Result and Evaluation are separate concepts

**Date**: 2026-08-17

**Decision**:
`Result` represents what happened during execution (output, error, agent_id), while `Evaluation` represents ABOS's assessment of that execution (quality_score, correctness_score, latency_ms, feedback).

**Reason**:
Agents produce Results; ABOS evaluates Results separately. Mixing evaluation scores into Result would violate single responsibility and force agents to self-evaluate.

**Consequences**:
Agents remain focused on task execution, while downstream evaluator services can independently assess quality.

---

## Decision 7: Execution represents one attempt, allowing multiple executions per Task

**Date**: 2026-08-17

**Decision**:
`Execution` encapsulates a single execution attempt of a Task by an Agent, with `attempt_number` and `ExecutionStatus`.

**Reason**:
A Task may undergo multiple execution attempts due to retries, timeouts, or failure recovery.

**Consequences**:
Retries and recovery strategies create distinct `Execution` instances linked to the same `Task`.

---

## Decision 8: AgentProfile stores quantitative historical performance

**Date**: 2026-08-17

**Decision**:
`AgentProfile` maintains historical metrics (`success_rate`, `avg_latency_ms`, `confidence_score`) per agent.

**Reason**:
Schedulers need historical performance metrics for intelligent agent selection.

**Consequences**:
Performance metrics are isolated in `AgentProfile` rather than polluting the `BaseAgent` contract.

---

## Decision 9: Future Scheduler reads AgentProfile while PerformanceTracker updates it

**Date**: 2026-08-17

**Decision**:
The future `Scheduler` will read `AgentProfile`, while `PerformanceTracker` will be the writer updating profiles based on `Evaluation` records.

**Reason**:
Prevents direct coupling between scheduling logic and performance tracking logic.

**Consequences**:
Maintains clean directional flow: Execution -> Result -> Evaluation -> PerformanceTracker -> AgentProfile -> Scheduler.

---

## Decision 10: LangGraph is an orchestration/runtime technology, not the ABOS domain model

**Date**: 2026-08-17

**Decision**:
LangGraph will be used as an orchestration framework in future milestones, but will not define core domain objects like `Task`, `Agent`, or `Result`.

**Reason**:
Preserves ABOS's fundamental domain identity and avoids framework lock-in.

**Consequences**:
ABOS domain model remains usable independent of the LangGraph runtime.
