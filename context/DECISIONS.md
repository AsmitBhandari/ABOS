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

---

## Decision 11: Planner is an orchestration component

**Date**: 2026-08-17

**Decision**:
The `Planner` abstraction resides in `orchestration/planner/` and operates on domain `Task` objects without embedding planning logic into `core/task.py`.

**Reason**:
Follows the Core Domain Independence rule. `Task` is a domain data structure; planning is an orchestration capability.

**Consequences**:
Preserves clean separation between data definitions and orchestration behavior.

---

## Decision 12: Planner does not select Agents

**Date**: 2026-08-17

**Decision**:
When generating subtasks, the Planner leaves `assigned_agent_id = None`.

**Reason**:
Agent selection is the distinct responsibility of the upcoming `Scheduler` (v0.4), which considers capabilities, availability, and `AgentProfile` performance scores.

**Consequences**:
Decouples planning from agent routing and avoids premature assignment.

---

## Decision 13: Deterministic Planner precedes LLM Planner

**Date**: 2026-08-17

**Decision**:
Implement `DeterministicPlanner` before introducing LLM-based planning.

**Reason**:
Allows architectural validation of task decomposition, hierarchy construction, and validation mechanics independently of external model behavior or API dependencies.

**Consequences**:
Establishes a solid, testable baseline interface that a future `LLMPlanner` can drop into without modifying domain contracts.

---

## Decision 14: PlanningResult is separate from Task

**Date**: 2026-08-17

**Decision**:
`Planner.plan()` returns a structured `PlanningResult` container (`task_id`, `should_decompose`, `subtasks`, `reason`, `confidence`, `valid`, `metadata`) rather than mutating `Task` in-place.

**Reason**:
Task represents a unit of work, while `PlanningResult` represents the planner's decision and reasoning.

**Consequences**:
Orchestration callers can inspect planning decisions, confidence, and validation status explicitly.

---

## Decision 15: Planner supports hierarchical Tasks

**Date**: 2026-08-17

**Decision**:
When decomposition occurs, `Planner` links children to the parent via `child.parent_task_id = parent.id` and `parent.child_task_ids = [child.id, ...]`.

**Reason**:
Preserves full structural provenance of composite tasks across the execution pipeline.

**Consequences**:
Enables multi-step execution graphs and hierarchy inspection downstream.

---

## Decision 16: Scheduler is an orchestration component

**Date**: 2026-08-18

**Decision**:
The `Scheduler` abstraction resides in `orchestration/scheduler/` and operates on domain `Task`, `BaseAgent`, and `AgentProfile` objects without embedding scheduler logic or state into `core/`.

**Reason**:
Agent selection and performance ranking are orchestration concerns, not domain data structures. Core domain objects must remain independent of scheduling logic.

**Consequences**:
Preserves clean separation between domain models and orchestration behavior.

---

## Decision 17: Capability filtering occurs before performance scoring

**Date**: 2026-08-18

**Decision**:
An agent whose capabilities do not satisfy the task's required capabilities is rejected immediately during filtering and is not scored for performance.

**Reason**:
An agent that cannot execute a task should not be ranked as a "low-performing candidate" or accidentally selected if other metrics happen to be high.

**Consequences**:
Only agents that possess all required capabilities and are in `IDLE` state proceed to performance scoring.

---

## Decision 18: AgentProfile is read-only to Scheduler

**Date**: 2026-08-18

**Decision**:
The `Scheduler` strictly reads historical performance metrics from `AgentProfile` and never creates, mutates, or persists profiles.

**Reason**:
Historical performance records must be maintained and updated exclusively by the future `PerformanceTracker` (v0.5) following task evaluations, preventing circular dependencies or premature profile mutations.

**Consequences**:
Maintains strict one-way data flow: Execution -> Result -> Evaluation -> PerformanceTracker -> AgentProfile -> Scheduler.

---

## Decision 19: Default performance scoring weights

**Date**: 2026-08-18

**Decision**:
Default performance scoring uses the weights: `success_rate: 0.50`, `latency_score: 0.20`, `confidence_score: 0.30` (summing to 1.00), with support for configurable `ScoringPolicy` instances.

**Reason**:
Provides a transparent, explainable, and research-ready baseline that balances correctness (success rate), speed (latency), and model certainty (confidence).

**Consequences**:
Enables benchmarking and comparative experiments across different scheduling policies without modifying scheduler contracts.

---

## Decision 20: Scheduling and tie-breaking are deterministic

**Date**: 2026-08-18

**Decision**:
`DeterministicScheduler` uses a multi-tier deterministic tie-breaking sequence (total score -> success rate -> confidence score -> lowest latency -> lexicographical agent ID) with zero randomness or LLM reliance.

**Reason**:
Determinism and reproducibility are essential for debugging, systematic testing, and scientific research evaluation.

**Consequences**:
The same inputs (`Task`, `agents`, `profiles`, `policy`) will always produce the identical `SchedulingResult`.

---

## Decision 21: SchedulingResult is separate from Task mutation

**Date**: 2026-08-18

**Decision**:
The `Scheduler` returns a structured `SchedulingResult` containing `selected_agent_id`, `success`, `reason`, `score`, and `candidates` without mutating `task.assigned_agent_id` or agent state in-place.

**Reason**:
Making a scheduling decision is distinct from executing the assignment or transitioning agent lifecycle states.

**Consequences**:
Callers can inspect scheduling decisions, candidate breakdowns, and reasons before committing to task execution or lifecycle state transitions.

---

## Decision 22: Evaluation remains separate from performance history

**Date**: 2026-08-20

**Decision**:
`Evaluation` represents an assessment of a single execution attempt, while `AgentProfile` stores cumulative historical performance metrics.

**Reason**:
Conflating single-attempt evaluation with historical tracking would violate single responsibility and prevent multiple independent evaluation strategies.

**Consequences**:
Maintains clean separation between individual execution assessments and long-term agent profiles.

---

## Decision 23: PerformanceTracker owns AgentProfile updates

**Date**: 2026-08-20

**Decision**:
`PerformanceTracker` resides in the orchestration layer (`orchestration/performance/tracker.py`) and is the sole component authorized to update `AgentProfile` records from `Evaluation` records.

**Reason**:
Follows the Core Domain Independence rule. `AgentProfile` is a domain data structure; converting evaluations into historical statistics is an orchestration capability. Schedulers remain read-only consumers.

**Consequences**:
Prevents tight coupling between domain entities, schedulers, and evaluation systems.

---

## Decision 24: Success rate uses exact cumulative counts

**Date**: 2026-08-20

**Decision**:
`AgentProfile.success_rate` is updated using exact cumulative counters (`successful_executions / total_executions`) without rolling windows or exponential decay in v0.5.

**Reason**:
Provides transparent, deterministic, and easily verifiable metrics for scientific baseline evaluation.

**Consequences**:
Every execution contributes equally to the historical success rate.

---

## Decision 25: Latency uses an incremental cumulative average

**Date**: 2026-08-20

**Decision**:
`AgentProfile.avg_latency_ms` is updated using the incremental cumulative average formula: `((old_avg * old_count) + new_latency) / (old_count + 1)`.

**Reason**:
Enables O(1) memory and computation updates without requiring storage of full historical latency time-series.

**Consequences**:
Efficient in-memory performance tracking that scales without unbound memory growth.

---

## Decision 26: Confidence score represents evidence strength rather than agent quality

**Date**: 2026-08-20

**Decision**:
`confidence_score` is computed as `min(1.0, total_executions / confidence_saturation)` (default saturation = 20), rather than mirroring `success_rate` or agent quality.

**Reason**:
Confidence reflects the statistical reliability and quantity of observations collected, whereas `success_rate` reflects observed task success. A low-performing agent with 50 executions has high confidence in its low score.

**Consequences**:
Scheduler can distinguish between unproven agents (low confidence) and thoroughly evaluated agents (high confidence).

---

## Decision 27: Scheduler scoring policy weights remain fixed in v0.5

**Date**: 2026-08-20

**Decision**:
Scheduler scoring policy weights (success: 0.50, latency: 0.20, confidence: 0.30) remain fixed during runtime. ABOS adapts through updated `AgentProfile` metrics rather than self-modifying scheduler weights.

**Reason**:
Ensures explainability, determinism, and controlled comparative experimentation without unconstrained policy drift.

**Consequences**:
Adaptation is strictly driven by empirical observation updates to candidate agent profiles.

---

## Decision 28: Failed executions remain valid performance observations

**Date**: 2026-08-20

**Decision**:
When an execution fails (`success = False`), `PerformanceTracker` increments `total_executions`, leaves `successful_executions` unchanged, and records the observed latency.

**Reason**:
Failure is a crucial signal of real-world agent reliability and efficiency. Ignoring failures would skew metrics positively.

**Consequences**:
Agent success rate and average latency accurately reflect overall execution history.

---

## Decision 29: Evaluation updates are idempotent by Evaluation ID

**Date**: 2026-08-20

**Decision**:
`PerformanceTracker` tracks processed `evaluation.id` strings in memory and ignores duplicate submissions of the same evaluation ID without altering profile statistics.

**Reason**:
Prevents duplicated network messages or retry loops from corrupting statistical counts.

**Consequences**:
Safe execution in distributed or retry-prone environments without double-counting observations.

---

## Decision 30: Agent specialization is capability-based

**Date**: 2026-08-20

**Decision**:
Specialized agents (`CalculatorAgent`, `TextAnalysisAgent`, `UnitConversionAgent`) share the identical abstract `BaseAgent` contract (`execute(task: Task) -> Result`) and differentiate themselves exclusively via declared capability strings (`capabilities: List[str]`).

**Reason**:
Prevents exploding base class hierarchies or concrete type dependencies inside `Scheduler` and `Orchestrator`. Task routing is determined purely by matching `task.required_capabilities` against `agent.capabilities`.

**Consequences**:
New specialized agent implementations can be seamlessly registered and routed without modifying core domain contracts, planner logic, or scheduler selection algorithms.


