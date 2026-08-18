# ABOS Project Context

## Project Name
Adaptive Behavior Operating System (ABOS)

## Project Purpose
ABOS is a research project designed to explore adaptive, modular, and autonomous agent orchestration. The long-term goal is to build an operating system-like architecture that coordinates heterogeneous execution strategies (deterministic, rule-based, ML models, and LLM-driven agents) for multi-step task resolution.

## Research Objective
Investigate scalable agent abstractions, dynamic task routing, capability discovery, persistent memory systems, and runtime execution monitoring without tight coupling to specific AI or LLM providers.

## Current Development Phase
**Phase 4: Scheduler & Agent Selection (v0.4 - Implemented & Verified)**

## Core Architecture Layers
1. **Core Domain Contracts (`core/`)**:
   - `Task`: Unit of work supporting atomic and composite parent/child task hierarchies.
   - `BaseAgent`: Abstract contract for execution entities with capability and operational state tracking.
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
   - `Scheduler` (`BaseScheduler`): Contract for performance-aware agent selection.
   - `SchedulingResult` & `CandidateScore`: Structured scheduling decision and candidate breakdown containers.
   - `DeterministicScheduler`: Deterministic capability matching, state filtering, and performance scoring engine.
   - `ScoringPolicy`: Configurable weighting policy and latency normalization for agent ranking.
   - `Orchestrator`: Capability-based task router (`core/orchestrator.py`).

## Core Architectural Principles
- **Core Domain Independence**: Core objects must contain domain information, not infrastructure concerns.
- **Planner Separation**: Planner is an orchestration component; it generates task structure without assigning or executing agents.
- **Scheduler Separation**: Scheduler is an orchestration component; it evaluates capabilities, agent states, and historical profiles to select agents without mutating domain objects or executing agents.
- **Read-Only Profile Access**: Scheduler reads `AgentProfile` metrics for routing decisions; updating profiles is strictly deferred to the future `PerformanceTracker` (v0.5).
- **Framework Agnostic**: Pure Python standard library implementation without lock-in to FastAPI, LangGraph, LiteLLM, PostgreSQL, or Redis.
- **Result vs Evaluation Separation**: Agents produce Results; ABOS evaluates Results separately.

## Implemented vs Planned Architecture
- **IMPLEMENTED (v0.4)**: Seven core domain contracts, Planner subsystem (`Planner`, `PlanningResult`, `DeterministicPlanner`, `DecompositionValidator`), Scheduler subsystem (`Scheduler`, `SchedulingResult`, `CandidateScore`, `DeterministicScheduler`, `ScoringPolicy`), `Orchestrator`, `CalculatorAgent`, unit test suite (80 tests).
- **PLANNED**: Evaluator service & PerformanceTracker adaptive loop (v0.5), Recovery & Memory (v0.6), LangGraph orchestration (v0.7), LLM Planner & external integrations (Later).
