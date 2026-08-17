# ABOS (Adaptive Behavior Operating System)

```text
ABOS v0.2
Core Domain Contracts
```

## 1. What is ABOS?

**ABOS (Adaptive Behavior Operating System)** is a research project exploring modular, extensible, and framework-independent multi-agent task execution. The goal of ABOS is to establish an operating-system-like abstraction layer that coordinates diverse execution strategies (deterministic rule engines, mathematical solvers, machine learning models, and LLM-driven agents) without hard-coding system logic to a specific vendor framework.

## 2. Current Development Phase

This repository represents **Phase 2: ABOS v0.2 (Core Domain Contracts)**.

The objective of v0.2 is to establish seven canonical core domain contracts that future ABOS components (Planner, Scheduler, Evaluator, Recovery, Memory, and LangGraph orchestration) can build against without framework lock-in.

## 3. Implemented vs Planned Architecture

### IMPLEMENTED (v0.2)

ABOS v0.2 establishes seven canonical core domain contracts in `core/`:

1. **`Task` (`core/task.py`)**: Unit of work. Supports atomic tasks and composite parent/child task hierarchies (`parent_task_id`, `child_task_ids`).
2. **`BaseAgent` (`core/agent.py`)**: Abstract base contract for all ABOS agents (`id`, `name`, `capabilities`, `state`, `execute(task)`).
3. **`BaseTool` (`core/tool.py`)**: Abstract base contract for external tools (`name`, `description`, `input_schema`, `execute`).
4. **`Result` (`core/result.py`)**: Structured outcome of a task execution produced by an agent (`success`, `output`, `error`, `agent_id`, `execution_id`, `metadata`).
5. **`Execution` (`core/execution.py`)**: Single attempt to execute a Task by an Agent (`task_id`, `agent_id`, `status`, `attempt_number`, `started_at`, `result`).
6. **`Evaluation` (`core/evaluation.py`)**: Assessment of an Execution produced separately by ABOS (`quality_score`, `correctness_score`, `latency_ms`, `feedback`).
7. **`AgentProfile` (`core/agent_profile.py`)**: Historical quantitative performance metrics per agent (`total_executions`, `successful_executions`, `success_rate`, `avg_latency_ms`, `confidence_score`).

Also implemented:
- **`CalculatorAgent` (`agents/calculator_agent.py`)**: Safe AST math evaluation.
- **`Orchestrator` (`core/orchestrator.py`)**: In-memory capability-matching task router.
- **Test Suite (`tests/`)**: 36 passing unit tests covering all core contracts.

### PLANNED / NOT YET IMPLEMENTED

Per project rules and milestone scope, the following are **PLANNED** for future milestones and are **NOT YET IMPLEMENTED** in this repository:
- Task Decomposition & Planner engine (Planned v0.3)
- Performance & Capability-based Scheduler v2 (Planned v0.4)
- Automated Evaluator service & PerformanceTracker adaptive loop (Planned v0.5)
- Recovery system & Persistent Memory integration (Planned v0.6)
- LangGraph Orchestration integration (Planned v0.7)
- FastAPI, LiteLLM, PostgreSQL, Redis, and Celery infrastructure (Planned Later)

## 4. Architectural Rules

ABOS enforces the following core principle:
> **Core objects must contain domain information, not infrastructure concerns.**

Core domain objects represent ABOS concepts independently of external frameworks and infrastructure.

## 5. Installation & Setup

ABOS v0.2 relies exclusively on the **Python 3 standard library**. No third-party dependencies are required.

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
=== ABOS v0.1: Core Foundation Prototype ===

Task:
  Description: Calculate 25 * 37
  Input Data:  25 * 37
  Priority:    HIGH

Orchestrator:
  Selecting suitable agent...
  Selected Agent: CalculatorAgent (ID: agent-calculator-01)

Executing task...

Result:
  Success:  True
  Output:   925
  Agent ID: agent-calculator-01
  Error:    None

Status:
  COMPLETED

=== Execution Complete ===
```

## 7. How to Run Tests

Run the full unit test suite using standard Python `unittest`:

```bash
python -m unittest discover -s tests
```
