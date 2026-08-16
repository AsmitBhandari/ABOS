# ABOS (Adaptive Behavior Operating System)

```text
ABOS v0.1
Core Foundation Prototype
```

## 1. What is ABOS?

**ABOS (Adaptive Behavior Operating System)** is a final-year research project exploring modular, extensible, and provider-independent multi-agent task execution. The goal of ABOS is to establish an operating-system-like abstraction layer that coordinates diverse execution strategies (deterministic rule engines, mathematical solvers, machine learning models, and LLM-driven agents) without hard-coding system logic to a specific vendor framework.

## 2. Current Development Phase

This repository represents **Phase 1: ABOS v0.1 (Core Foundation Prototype)**.

The objective of v0.1 is **not** to deliver a complete multi-agent AI system, but rather to establish a clean, typed, and well-tested architectural foundation that future developers can safely build upon.

## 3. Current Architecture

ABOS v0.1 establishes a decoupled task-routing pipeline:

```text
User / Input
     │
     ▼
   Task (input_data, priority, status)
     │
     ▼
Orchestrator (Agent Registration & Selection)
     │
     ▼
CalculatorAgent (Safe AST Math Evaluation)
     │
     ▼
  Result (success, output, error, metadata)
```

## 4. Four Core Abstractions

ABOS defines four fundamental building blocks in `core/`:

1. **`Task` (`core/task.py`)**: Represents a unit of work. Contains unique `id`, `description`, `input_data`, `priority`, `status` (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`), and optional `result`.
2. **`BaseAgent` (`core/agent.py`)**: Abstract base class defining `id`, `name`, `capabilities`, `state` (`IDLE`, `BUSY`, `ERROR`), and the `execute(task: Task) -> Result` interface.
3. **`BaseTool` (`core/tool.py`)**: Minimal provisional contract for external tools (`name`, `description`, `input_schema`, `execute(**kwargs)`).
4. **`Result` (`core/result.py`)**: Structured outcome returned by execution flows, containing `success`, `output`, `error`, `agent_id`, and `metadata`.

## 5. CalculatorAgent

`CalculatorAgent` (`agents/calculator_agent.py`) is the initial concrete agent created to validate the architecture.
- Evaluates arithmetic expressions (e.g. `25 * 37`) to return structured results (e.g. `925`).
- **Security**: Uses safe AST-node traversal (`SafeMathEvaluator`) without invoking unsafe Python `eval()`.
- Gracefully handles syntax errors, zero-division, and code injection attempts.

## 6. Orchestrator

`Orchestrator` (`core/orchestrator.py`) manages agent registration, selects matching agents based on required capabilities, executes tasks, and captures results or unexpected runtime errors into standard `Result` objects.

## 7. Installation & Setup

ABOS v0.1 relies exclusively on the **Python 3 standard library**. No external third-party dependencies are required.

```bash
# Prerequisites: Python 3.10+ installed
python --version
```

## 8. How to Run the Application

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

## 9. How to Run Tests

Run the full unit test suite using standard Python `unittest`:

```bash
python -m unittest discover -s tests
```

## 10. Current Limitations

- **Single Concrete Agent**: Only `CalculatorAgent` is implemented in v0.1 to validate baseline contracts.
- **In-Memory Orchestration**: Agents and registered tasks are managed in-memory per runtime execution.

## 11. Intentionally Not Implemented Yet

Per project rules and milestone scope, the following are intentionally omitted from v0.1:
- LLM API integrations (OpenAI, Gemini, Claude, etc.)
- Agent frameworks (LangChain, CrewAI, AutoGen)
- Persistent databases (PostgreSQL, Redis, MongoDB)
- Runtime Memory system (`memory/`)
- User Interface / Web Dashboard
- Docker / Cloud orchestration / Multi-node networking
