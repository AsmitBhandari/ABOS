# ABOS Project Context

## Project Name
Adaptive Behavior Operating System (ABOS)

## Project Purpose
ABOS is a research project designed to explore adaptive, modular, and autonomous agent orchestration. The long-term goal is to build an operating system-like architecture that coordinates heterogeneous execution strategies (deterministic, rule-based, ML models, and LLM-driven agents) for multi-step task resolution.

## Research Objective
Investigate scalable agent abstractions, dynamic task routing, capability discovery, persistent memory systems, and runtime execution monitoring without tight coupling to specific AI or LLM providers.

## Current Development Phase
**Phase 1: Core Foundation Prototype (v0.1)**

## Core Concept
A decoupled execution pipeline:
`Task` → `Orchestrator` → `Agent Selection` → `Agent (e.g., CalculatorAgent)` → `Result`

## Major Components
- **Task**: Representation of work to be accomplished.
- **Agent**: Abstract contract for execution entities.
- **Tool**: Standard interface for external capabilities accessible by agents.
- **Result**: Structured outcome of task execution.
- **Orchestrator**: Central coordinator for registering agents and executing tasks.

## Technology Choices
- **Language**: Python 3.10+
- **Standard Library Focus**: Minimal dependencies; utilizing `dataclasses`, `enum`, `abc`, `ast`, and `unittest`.
- **Framework Independence**: Zero external AI/LLM framework lock-in.

## Important Constraints
- Base Agent abstraction must remain LLM-independent.
- Tasks must not depend on specific agents.
- Arbitrary code execution (`eval()`) is strictly prohibited.
- Development context (`context/`) must remain separate from runtime memory (`memory/`).

## Current Milestone
Establish ABOS v0.1 core foundation, baseline contracts, test suite, and minimal CLI demonstration.
