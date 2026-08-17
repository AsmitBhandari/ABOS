# ABOS Project Context

## Project Name
Adaptive Behavior Operating System (ABOS)

## Project Purpose
ABOS is a research project designed to explore adaptive, modular, and autonomous agent orchestration. The long-term goal is to build an operating system-like architecture that coordinates heterogeneous execution strategies (deterministic, rule-based, ML models, and LLM-driven agents) for multi-step task resolution.

## Research Objective
Investigate scalable agent abstractions, dynamic task routing, capability discovery, persistent memory systems, and runtime execution monitoring without tight coupling to specific AI or LLM providers.

## Current Development Phase
**Phase 3: Planner & Task Decomposition (v0.3 - Implemented & Verified)**

## Core Architecture Layers
1. **Core Domain Contracts (`core/`)**:
   - `Task`: Unit of work supporting atomic and composite parent/child task hierarchies.
   - `BaseAgent`: Abstract contract for execution entities.
   - `BaseTool`: Interface for external tools/capabilities.
   - `Result`: Structured outcome of execution produced by an agent.
   - `Execution`: Single attempt to execute a Task.
   - `Evaluation`: ABOS's assessment of an Execution.
   - `AgentProfile`: Quantitative historical performance metrics.
2. **Orchestration Layer (`orchestration/`)**:
   - `Planner` (`BasePlanner`): Contract for assessing and decomposing tasks into subtask hierarchies.
   - `PlanningResult`: Structured planning decision container.
   - `DeterministicPlanner`: Rule-based deterministic decomposition engine.
   - `DecompositionValidator`: Structural validation of parent-child subtask relationships.
   - `Orchestrator`: Capability-based task router (`core/orchestrator.py`).

## Core Architectural Principles
- **Core Domain Independence**: Core objects must contain domain information, not infrastructure concerns.
- **Planner Separation**: Planner is an orchestration component; it generates task structure without assigning or executing agents.
- **Framework Agnostic**: Pure Python standard library implementation without lock-in to FastAPI, LangGraph, LiteLLM, PostgreSQL, or Redis.
- **Result vs Evaluation Separation**: Agents produce Results; ABOS evaluates Results separately.

## Implemented vs Planned Architecture
- **IMPLEMENTED (v0.3)**: Seven core domain contracts, Planner abstraction (`Planner`, `PlanningResult`), `DeterministicPlanner`, `DecompositionValidator`, `Orchestrator`, `CalculatorAgent`, unit test suite (53 tests).
- **PLANNED**: Capability & performance-based Scheduler (v0.4), Evaluator service & PerformanceTracker (v0.5), Recovery & Memory (v0.6), LangGraph orchestration (v0.7), LLM Planner & external integrations (Later).
