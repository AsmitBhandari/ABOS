# ABOS (Adaptive Behavior Operating System)

```text
ABOS v0.4
Scheduler + Performance-Aware Agent Selection
```

## 1. What is ABOS?

**ABOS (Adaptive Behavior Operating System)** is a research project exploring modular, extensible, and framework-independent multi-agent task execution. The goal of ABOS is to establish an operating-system-like abstraction layer that coordinates diverse execution strategies (deterministic rule engines, mathematical solvers, machine learning models, and LLM-driven agents) without hard-coding system logic to a specific vendor framework.

## 2. Current Development Phase

This repository represents **Phase 4: ABOS v0.4 (Scheduler + Agent Selection)**.

The objective of v0.4 is to establish the Scheduler orchestration layer, structured `SchedulingResult`, configurable `ScoringPolicy`, and `DeterministicScheduler` for performance-aware agent selection based on task capability requirements, agent availability, and quantitative `AgentProfile` metrics.

## 3. Implemented vs Planned Architecture

### IMPLEMENTED (v0.4)

#### Orchestration Layer (`orchestration/`)
1. **`Scheduler` (`BaseScheduler`) (`orchestration/scheduler/base.py`)**: Abstract base contract for performance-aware agent selection (`schedule(task, agents, profiles) -> SchedulingResult`).
2. **`SchedulingResult` & `CandidateScore` (`orchestration/scheduler/base.py`)**: Structured containers representing scheduling decisions, candidate rankings, and eligibility reasons.
3. **`ScoringPolicy` (`orchestration/scheduler/scoring.py`)**: Configurable weighting policy (default: 0.50 success rate, 0.20 latency, 0.30 confidence) with inverted min-max latency normalization and strict validation.
4. **`DeterministicScheduler` (`orchestration/scheduler/deterministic.py`)**: Deterministic agent selection engine executing capability filtering, state filtering (`IDLE`), profile performance scoring, and multi-tier deterministic tie-breaking.
5. **`Planner` (`BasePlanner`) (`orchestration/planner/base.py`)**: Abstract base contract for task planning and decomposition (`plan(task) -> PlanningResult`).
6. **`PlanningResult` (`orchestration/planner/base.py`)**: Structured container representing planning decisions (`task_id`, `should_decompose`, `subtasks`, `reason`, `confidence`, `valid`).
7. **`DeterministicPlanner` (`orchestration/planner/deterministic.py`)**: Rule-based decomposition engine that detects multi-step structures and generates child subtasks.
8. **`DecompositionValidator` (`orchestration/planner/validator.py`)**: Structural integrity validator for parent-child task hierarchies.
9. **`Orchestrator` (`core/orchestrator.py`)**: Capability-matching task router.

#### Core Domain Contracts (`core/`)
1. **`Task` (`core/task.py`)**: Unit of work supporting atomic tasks and composite parent/child task hierarchies (`parent_task_id`, `child_task_ids`).
2. **`BaseAgent` (`core/agent.py`)**: Abstract base contract for all ABOS agents (`id`, `name`, `capabilities`, `state`, `execute(task)`).
3. **`BaseTool` (`core/tool.py`)**: Abstract base contract for external tools (`name`, `description`, `input_schema`, `execute`).
4. **`Result` (`core/result.py`)**: Structured outcome of a task execution produced by an agent (`success`, `output`, `error`, `agent_id`, `execution_id`, `metadata`).
5. **`Execution` (`core/execution.py`)**: Single attempt to execute a Task by an Agent (`task_id`, `agent_id`, `status`, `attempt_number`, `started_at`, `result`).
6. **`Evaluation` (`core/evaluation.py`)**: Assessment of an Execution produced separately by ABOS (`quality_score`, `correctness_score`, `latency_ms`, `feedback`).
7. **`AgentProfile` (`core/agent_profile.py`)**: Historical quantitative performance metrics per agent (`total_executions`, `successful_executions`, `success_rate`, `avg_latency_ms`, `confidence_score`).

Also implemented:
- **`CalculatorAgent` (`agents/calculator_agent.py`)**: Safe AST math evaluation.
- **Test Suite (`tests/`)**: 80 passing unit tests covering all core contracts, planner subsystem, and scheduler subsystem.

### PLANNED / NOT YET IMPLEMENTED

Per project rules and milestone scope, the following are **PLANNED** for future milestones and are **NOT YET IMPLEMENTED** in this repository:
- Automated Evaluator service & PerformanceTracker adaptive loop (Planned v0.5)
- Recovery system & Persistent Memory integration (Planned v0.6)
- LangGraph Orchestration integration (Planned v0.7)
- LLM-based Planner (Planned v0.8)
- FastAPI, LiteLLM, PostgreSQL, Redis, and Celery infrastructure (Planned Later)

## 4. Architectural Rules

ABOS enforces the following core principle:
> **Core objects must contain domain information, not infrastructure concerns.**

Core domain objects represent ABOS concepts independently of external frameworks and infrastructure.

## 5. Installation & Setup

ABOS v0.4 relies exclusively on the **Python 3 standard library**. No third-party dependencies are required.

```bash
# Prerequisites: Python 3.10+ installed
python --version
```

## 6. How to Run the Application

Run `main.py` from the project root directory:

```bash
python main.py
```

### Example Console Output:
```text
=== ABOS v0.4: Scheduler & Performance-Aware Agent Selection ===

Task: 'Analyze telemetry data and compute statistics'
  Required Capabilities: ['python']

Candidate Agents & Historical Profiles:
  - [agent-python-alpha] DataProcessor-Alpha: caps=['python', 'math'], state=IDLE | Success: 98%, Latency: 85.0ms, Conf: 0.95
  - [agent-python-beta] DataProcessor-Beta: caps=['python'], state=IDLE | Success: 76%, Latency: 320.0ms, Conf: 0.7
  - [agent-research-gamma] ResearchAgent-Gamma: caps=['research'], state=IDLE | Success: 95%, Latency: 110.0ms, Conf: 0.9

Scheduling Result:
  Success:           True
  Selected Agent ID: agent-python-alpha
  Score:             0.975
  Reason:            Selected agent 'agent-python-alpha' with highest performance score (0.975).

Candidate Breakdown:
  - [agent-python-alpha] Total Score: 0.9750 | ELIGIBLE
  - [agent-python-beta] Total Score: 0.5900 | ELIGIBLE
  - [agent-research-gamma] Total Score: 0.0000 | REJECTED (Missing required capabilities: ['python'])

=== ABOS v0.1: CalculatorAgent Task Execution Flow ===

Task: Calculate 25 * 37 (Input: 25 * 37)
Selected Agent: CalculatorAgent (agent-calculator-01)
Result: Success=True, Output=925, Error=None
Task Status: COMPLETED

=== ABOS Demonstration Complete ===
```

## 7. How to Run Tests

Run the full unit test suite using standard Python `unittest`:

```bash
python -m unittest discover -s tests
```
