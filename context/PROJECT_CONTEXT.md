# ABOS Project Context

## Project Name
Adaptive Behavior Operating System (ABOS)

## Project Purpose
ABOS is a research project designed to explore adaptive, modular, and autonomous agent orchestration. The long-term goal is to build an operating system-like architecture that coordinates heterogeneous execution strategies (deterministic, rule-based, ML models, and LLM-driven agents) for multi-step task resolution.

## Research Objective
Investigate scalable agent abstractions, dynamic task routing, capability discovery, persistent memory systems, and runtime execution monitoring without tight coupling to specific AI or LLM providers.

## Current Development Phase
**Phase 2: Core Domain Contracts (v0.2 - Implemented & Verified)**

## Core Domain Contracts (Seven Canonical Objects)
1. **Task**: Unit of work (supports atomic tasks & composite parent/child task hierarchies).
2. **Agent**: Abstract contract (`BaseAgent`) for execution entities.
3. **Tool**: Interface (`BaseTool`) for external capabilities accessible by agents.
4. **Result**: Structured outcome of task execution produced by an agent (separate from evaluation).
5. **Execution**: Single attempt to execute a Task (`attempt_number`, `ExecutionStatus`).
6. **Evaluation**: ABOS's assessment of an Execution (`quality_score`, `correctness_score`, `latency_ms`).
7. **AgentProfile**: Quantitative historical performance metrics (`confidence_score`, `success_rate`, `avg_latency_ms`).

## Core Architectural Principles
- **Core Domain Independence**: Core objects must contain domain information, not infrastructure concerns.
- **Framework Agnostic**: Core domain objects must remain usable independent of FastAPI, LangGraph, LiteLLM, PostgreSQL, or Redis.
- **Result vs Evaluation Separation**: Agents produce Results; ABOS evaluates Results separately.
- **Quantitative Adaptation**: Future Schedulers read `AgentProfile`; future `PerformanceTracker` updates `AgentProfile`.

## Technology Choices
- **Language**: Python 3.10+
- **Standard Library Focus**: Minimal dependencies; utilizing `dataclasses`, `enum`, `abc`, `ast`, `datetime`, `uuid`, and `unittest`.
- **Framework Independence**: Zero external framework lock-in.

## Important Constraints
- Core domain objects must not directly import external frameworks.
- Tasks must not depend on specific agents.
- Arbitrary code execution (`eval()`) is strictly prohibited.
- Development context (`context/`) must remain separate from runtime memory (`memory/`).

## Implemented vs Planned Architecture
- **IMPLEMENTED (v0.2)**: Core domain contracts (Task, Agent, Tool, Result, Execution, Evaluation, AgentProfile), Orchestrator, CalculatorAgent, unit test suite (36 tests).
- **PLANNED**: Planner & task decomposition engine (v0.3), capability/performance Scheduler (v0.4), Evaluator service & PerformanceTracker (v0.5), Recovery & Memory (v0.6), LangGraph orchestration (v0.7), FastAPI/PostgreSQL/Redis integration (Later).
