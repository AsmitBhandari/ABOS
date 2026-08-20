# ABOS Architecture

This document reflects the **actual implemented architecture** of ABOS v0.5 (Pre-Release).

## System Overview

ABOS establishes a complete, closed-loop adaptive orchestration architecture featuring the **Planner** (task decomposition), **Scheduler** (performance-aware agent selection), and **PerformanceTracker** (evaluation ingestion and historical profile updates) on top of the framework-independent domain layer and multi-agent ecosystem.

```mermaid
flowchart TD
    User([User / CLI]) -->|Task| Planner[Planner]
    Planner -->|Assess & Validate| PlanningResult[PlanningResult]
    PlanningResult -->|Atomic Task or Subtasks| TaskQueue[Task / Subtasks]
    TaskQueue --> Scheduler[Scheduler]
    AgentProfile[(AgentProfile)] -->|Reads Metrics| Scheduler
    Scheduler -->|Rank & Select| SchedulingResult[SchedulingResult]
    SchedulingResult -->|Selected Agent ID| Orchestrator[Orchestrator / Runtime]
    Orchestrator --> AgentPool[Agent Pool]
    AgentPool --> CalculatorAgent[CalculatorAgent (math)]
    AgentPool --> TextAnalysisAgent[TextAnalysisAgent (text_analysis)]
    AgentPool --> UnitConversionAgent[UnitConversionAgent (unit_conversion)]
    AgentPool -->|Executes| Execution[Execution]
    Execution --> Result[Result]
    Execution --> Evaluation[Evaluation]
    Evaluation -->|Ingests Assessment| PerformanceTracker[PerformanceTracker]
    PerformanceTracker -->|Updates Cumulative Metrics| AgentProfile
```

---

## 1. Agent Ecosystem (`agents/`) [IMPLEMENTED]

All ABOS agents share the common abstract contract `BaseAgent` (`core/agent.py`) and declare their capabilities:

```text
BaseAgent (core/agent.py)
   ├── CalculatorAgent (agents/calculator_agent.py)       -> capabilities: ["math", "calculation", "arithmetic"]
   ├── TextAnalysisAgent (agents/text_analysis_agent.py)   -> capabilities: ["text_analysis"]
   └── UnitConversionAgent (agents/unit_conversion_agent.py) -> capabilities: ["unit_conversion"]
```

### Capability-Based Specialization Principle
- **Unified Contract**: Every agent implements `execute(task: Task) -> Result`.
- **Capability Discovery**: Schedulers and orchestrators route tasks by checking whether `task.required_capabilities ⊆ agent.capabilities`.
- **No Class Coupling**: The orchestration layer does not depend on concrete agent classes, allowing any new capability or agent to be added without modifying the core or orchestration layers.

---

## 2. Orchestration Layer (`orchestration/`)

### Performance Tracking Subsystem (`orchestration/performance/`) [IMPLEMENTED]
- **`PerformanceTracker` (`orchestration/performance/tracker.py`)**: Converts single-execution assessments (`Evaluation`) into updated historical performance records (`AgentProfile`).
- **Tracker Pipeline (`update(evaluation, profile) -> AgentProfile`)**:
  1. **Agent ID Consistency Check**: Rejects updates where `evaluation.agent_id != profile.agent_id`.
  2. **In-Memory Idempotency**: Tracks processed `evaluation.id` to prevent double-counting.
  3. **Cumulative Execution Counts**:
     - `total_executions += 1`
     - `successful_executions += (1 if evaluation.success else 0)`
     - `success_rate = successful_executions / total_executions`
  4. **Incremental Cumulative Average Latency**:
     - `new_avg = ((old_avg * old_count) + new_latency) / new_count`
  5. **Evidence-Based Confidence Score**:
     - `confidence_score = min(1.0, total_executions / confidence_saturation)` (default: 20).
  6. **Quality & Correctness Aggregation**:
     - Stored under `profile.metadata["performance"]` as running cumulative averages.
  7. **Timestamp Update**:
     - Updates `profile.last_execution_at` from `evaluation.created_at`.

### Scheduler Subsystem (`orchestration/scheduler/`) [IMPLEMENTED]
- **`Scheduler` (`BaseScheduler`) (`orchestration/scheduler/base.py`)**: Contract for performance-aware agent selection.
- **`CandidateScore` (`orchestration/scheduler/base.py`)**: Record of candidate evaluation.
- **`SchedulingResult` (`orchestration/scheduler/base.py`)**: Container communicating the scheduling decision and candidate breakdown.
- **`ScoringPolicy` (`orchestration/scheduler/scoring.py`)**: Fixed weighting policy (`success_rate=0.50`, `latency=0.20`, `confidence=0.30`) with inverted min-max latency normalization.
- **`DeterministicScheduler` (`orchestration/scheduler/deterministic.py`)**: Deterministic capability matching, state filtering (`IDLE`), profile performance scoring, and deterministic tie-breaking.

### Planner Subsystem (`orchestration/planner/`) [IMPLEMENTED]
- **`Planner` (`BasePlanner`) (`orchestration/planner/base.py`)**: Contract defining `plan(task) -> PlanningResult`.
- **`PlanningResult` (`orchestration/planner/base.py`)**: Structured planning decision container.
- **`DeterministicPlanner` (`orchestration/planner/deterministic.py`)**: Rule-based decomposition engine.
- **`DecompositionValidator` (`orchestration/planner/validator.py`)**: Structural integrity validator.

### Orchestrator (`core/orchestrator.py`) [IMPLEMENTED]
- Central coordinator maintaining agent registration and capability-based task execution for atomic tasks.

---

## 3. Canonical Core Domain Contracts (`core/`)

1. **Task (`core/task.py`)** [IMPLEMENTED]: Unit of work with parent/child hierarchical support (`parent_task_id`, `child_task_ids`).
2. **Agent (`core/agent.py`)** [IMPLEMENTED]: Abstract contract (`BaseAgent`) with `execute(task: Task) -> Result` and operational state (`IDLE`, `BUSY`, `ERROR`, `TERMINATED`).
3. **Tool (`core/tool.py`)** [IMPLEMENTED]: Abstract contract (`BaseTool`) for external capabilities.
4. **Result (`core/result.py`)** [IMPLEMENTED]: Structured outcome of execution produced by an Agent.
5. **Execution (`core/execution.py`)** [IMPLEMENTED]: Single execution attempt of a Task.
6. **Evaluation (`core/evaluation.py`)** [IMPLEMENTED]: Separate assessment of an Execution.
7. **AgentProfile (`core/agent_profile.py`)** [IMPLEMENTED]: Historical quantitative performance record.

---

## 4. Future Architecture (NOT YET IMPLEMENTED)

- **Recovery System & Failure Handling** [PLANNED - v0.6]
- **Persistent Memory Subsystem** [PLANNED - v0.7]
- **LangGraph Workflow Orchestration** [PLANNED - v0.8]
- **LLM-Based Planner Integration** [PLANNED - v0.9]
- **Autonomous Scheduler Weight Adaptation / Meta-Learning** [PLANNED - Later]
- **FastAPI / LiteLLM / PostgreSQL / Redis Integration** [PLANNED - Later]
