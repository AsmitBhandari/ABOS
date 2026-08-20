# ABOS (Adaptive Behavior Operating System)

```text
ABOS v0.5 (Pre-Release)
Evaluation + Performance Tracking + Multi-Agent Adaptive Routing
```

## 1. What is ABOS?

**ABOS (Adaptive Behavior Operating System)** is a research project exploring modular, extensible, and framework-independent multi-agent task execution. The goal of ABOS is to establish an operating-system-like abstraction layer that coordinates diverse execution strategies (deterministic rule engines, mathematical solvers, text processing agents, unit converters, and machine learning models) without hard-coding system logic to a specific vendor framework.

## 2. Current Development Phase

This repository represents **Phase 5: ABOS v0.5 (Pre-Release Validation)**.

The objective of v0.5 is to establish the first genuine **adaptive feedback loop** in ABOS and validate it across heterogeneous specialized agents:
```text
Task → Planner → Scheduler → Agent Pool → Execution → Result → Evaluation → PerformanceTracker → AgentProfile → Scheduler
```
In this loop:
- `Execution` records a single execution attempt.
- `Result` records what happened during execution.
- `Evaluation` assesses the quality and efficiency of the execution.
- `PerformanceTracker` updates historical metrics in `AgentProfile` (success rate, average latency, evidence-based confidence, and aggregate quality/correctness).
- `Scheduler` reads the updated `AgentProfile` to make future performance-aware selection decisions.

## 3. Implemented vs Planned Architecture

### IMPLEMENTED (v0.5 Pre-Release)

#### Canonical Agent Ecosystem (`agents/`)
1. **`CalculatorAgent` (`agents/calculator_agent.py`)**: Safe AST arithmetic evaluation (capabilities: `math`, `calculation`, `arithmetic`).
2. **`TextAnalysisAgent` (`agents/text_analysis_agent.py`)**: Deterministic text analysis and word counting (capability: `text_analysis`).
3. **`UnitConversionAgent` (`agents/unit_conversion_agent.py`)**: Deterministic metric length conversions (capability: `unit_conversion`).

#### Orchestration Layer (`orchestration/`)
1. **`PerformanceTracker` (`orchestration/performance/tracker.py`)**: Orchestration component that ingests `Evaluation` records, enforces in-memory evaluation idempotency, and deterministically updates cumulative `AgentProfile` metrics.
2. **`Scheduler` (`BaseScheduler`) (`orchestration/scheduler/base.py`)**: Abstract base contract for performance-aware agent selection (`schedule(task, agents, profiles) -> SchedulingResult`).
3. **`SchedulingResult` & `CandidateScore` (`orchestration/scheduler/base.py`)**: Structured containers representing scheduling decisions, candidate rankings, and eligibility reasons.
4. **`ScoringPolicy` (`orchestration/scheduler/scoring.py`)**: Configurable weighting policy (default: 0.50 success rate, 0.20 latency, 0.30 confidence) with inverted min-max latency normalization and strict validation.
5. **`DeterministicScheduler` (`orchestration/scheduler/deterministic.py`)**: Deterministic agent selection engine executing capability filtering, state filtering (`IDLE`), profile performance scoring, and multi-tier deterministic tie-breaking.
6. **`Planner` (`BasePlanner`) (`orchestration/planner/base.py`)**: Abstract base contract for task planning and decomposition (`plan(task) -> PlanningResult`).
7. **`PlanningResult` (`orchestration/planner/base.py`)**: Structured container representing planning decisions (`task_id`, `should_decompose`, `subtasks`, `reason`, `confidence`, `valid`).
8. **`DeterministicPlanner` (`orchestration/planner/deterministic.py`)**: Rule-based decomposition engine that detects multi-step structures and generates child subtasks.
9. **`DecompositionValidator` (`orchestration/planner/validator.py`)**: Structural integrity validator for parent-child task hierarchies.
10. **`Orchestrator` (`core/orchestrator.py`)**: Capability-matching task router.

#### Core Domain Contracts (`core/`)
1. **`Task` (`core/task.py`)**: Unit of work supporting atomic tasks and composite parent/child task hierarchies (`parent_task_id`, `child_task_ids`).
2. **`BaseAgent` (`core/agent.py`)**: Abstract base contract for all ABOS agents (`id`, `name`, `capabilities`, `state`, `execute(task)`).
3. **`BaseTool` (`core/tool.py`)**: Abstract base contract for external tools (`name`, `description`, `input_schema`, `execute`).
4. **`Result` (`core/result.py`)**: Structured outcome of a task execution produced by an agent (`success`, `output`, `error`, `agent_id`, `execution_id`, `metadata`).
5. **`Execution` (`core/execution.py`)**: Single attempt to execute a Task by an Agent (`task_id`, `agent_id`, `status`, `attempt_number`, `started_at`, `result`).
6. **`Evaluation` (`core/evaluation.py`)**: Assessment of an Execution produced separately by ABOS (`quality_score`, `correctness_score`, `latency_ms`, `feedback`).
7. **`AgentProfile` (`core/agent_profile.py`)**: Historical quantitative performance metrics per agent (`total_executions`, `successful_executions`, `success_rate`, `avg_latency_ms`, `confidence_score`).

Also implemented:
- **Test Suite (`tests/`)**: 116 passing unit tests covering all core contracts, three specialized agents, planner subsystem, scheduler subsystem, performance tracker, and multi-agent adaptive routing.

### PLANNED / NOT YET IMPLEMENTED

Per project rules and milestone scope, the following are **PLANNED** for future milestones and are **NOT YET IMPLEMENTED** in this repository:
- Recovery system & Failure Handling (Planned v0.6)
- Persistent Memory integration (Planned v0.7)
- LangGraph Orchestration integration (Planned v0.8)
- LLM-based Planner (Planned v0.9)
- Automated Scheduler weight learning / Reinforcement Learning (Future Research)
- FastAPI, LiteLLM, PostgreSQL, Redis, and Celery infrastructure (Planned Later)

## 4. Architectural Rules

ABOS enforces the following core principle:
> **Core objects must contain domain information, not infrastructure concerns.**

Core domain objects represent ABOS concepts independently of external frameworks and infrastructure.

## 5. Installation & Setup

ABOS relies exclusively on the **Python 3 standard library**. No third-party dependencies are required.

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
=== ABOS Multi-Agent Execution Demonstration ===

1. Task: Calculate 25 * 37
   Selected Agent: CalculatorAgent (agent-calculator-01)
   Result: Success=True, Output=925, Status=COMPLETED

2. Task: Count words in sentence (Input: 'ABOS is an adaptive operating system')
   Selected Agent: TextAnalysisAgent (agent-text-01)
   Result: Success=True, Output=6 words, Status=COMPLETED

3. Task: Convert 5 km to m (Input: '5 km to m')
   Selected Agent: UnitConversionAgent (agent-unit-01)
   Result: Success=True, Output=5000 m, Status=COMPLETED

=== ABOS v0.5: Adaptive Feedback Loop & Performance Tracking ===

1. Initial Scheduling Decision: Selected 'agent-text-alpha' (Score: 0.8500)
   Alpha Profile: Success=100%, Latency=40.0ms, Conf=0.50
   Beta Profile:  Success=90%, Latency=75.0ms, Conf=1.00

2. Execution Failures & Evaluations Ingested for 'agent-text-alpha' (Success=False, Latency=350ms, 400ms)
3. PerformanceTracker Updated AgentProfile 'agent-text-alpha':
   Updated Alpha: Success=83.3%, Latency=95.8ms, Conf=0.60

4. Adapted Scheduling Decision: Selected 'agent-text-beta' (Score: 0.9500)
   Reason: Selected agent 'agent-text-beta' with highest performance score (0.95).

=== ABOS Demonstration Complete ===
```

## 7. How to Run Tests

Run the full unit test suite using standard Python `unittest`:

```bash
python -m unittest discover -s tests
```
