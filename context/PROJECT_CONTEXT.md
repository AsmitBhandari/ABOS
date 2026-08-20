# ABOS Project Context

## Project Name
Adaptive Behavior Operating System (ABOS)

## Project Purpose
ABOS is a research project designed to explore adaptive, modular, and autonomous agent orchestration. The long-term goal is to build an operating system-like architecture that coordinates heterogeneous execution strategies (deterministic, rule-based, ML models, and LLM-driven agents) for multi-step task resolution.

## Research Objective
Investigate scalable agent abstractions, dynamic task routing, capability discovery, persistent memory systems, and runtime execution monitoring without tight coupling to specific AI or LLM providers.

## Current Development Phase
**Phase 5: Evaluation + Performance Tracking + Adaptive Agent Profiles (v0.5 - Pre-Release Validation Complete)**

## Core Architecture Layers
1. **Core Domain Contracts (`core/`)**:
   - `Task`: Unit of work supporting atomic and composite parent/child task hierarchies.
   - `BaseAgent`: Abstract contract for execution entities with capability and operational state tracking.
   - `BaseTool`: Interface for external tools/capabilities.
   - `Result`: Structured outcome of execution produced by an agent.
   - `Execution`: Single attempt to execute a Task.
   - `Evaluation`: ABOS's assessment of an Execution.
   - `AgentProfile`: Quantitative historical performance metrics.
2. **Canonical Agents (`agents/`)**:
   - `CalculatorAgent`: Safe AST arithmetic evaluation (capabilities: `math`, `calculation`, `arithmetic`).
   - `TextAnalysisAgent`: Deterministic text processing and word counting (capability: `text_analysis`).
   - `UnitConversionAgent`: Deterministic metric length conversions (capability: `unit_conversion`).
3. **Orchestration Layer (`orchestration/`)**:
   - `Planner` (`BasePlanner`): Contract for assessing and decomposing tasks into subtask hierarchies.
   - `PlanningResult`: Structured planning decision container.
   - `DeterministicPlanner`: Rule-based deterministic decomposition engine.
   - `DecompositionValidator`: Structural validation of parent-child subtask relationships.
   - `Scheduler` (`BaseScheduler`): Contract for performance-aware agent selection.
   - `SchedulingResult` & `CandidateScore`: Structured scheduling decision and candidate breakdown containers.
   - `DeterministicScheduler`: Deterministic capability matching, state filtering, and performance scoring engine.
   - `ScoringPolicy`: Configurable weighting policy and latency normalization for agent ranking.
   - `PerformanceTracker`: Orchestration component that ingests `Evaluation` records and deterministically updates `AgentProfile` historical metrics.
   - `Orchestrator`: Capability-based task router (`core/orchestrator.py`).

## Core Architectural Principles
- **Core Domain Independence**: Core objects must contain domain information, not infrastructure concerns.
- **Capability-Based Specialization**: Agents specialize through declared capabilities rather than custom base classes, sharing the unified `BaseAgent` contract (`execute(task) -> Result`).
- **Planner Separation**: Planner generates task structure without assigning or executing agents.
- **Scheduler Separation**: Scheduler evaluates capabilities, agent states, and historical profiles to select agents without mutating domain objects or executing agents.
- **Read-Only Profile Access**: Scheduler reads `AgentProfile` metrics for routing decisions; updating profiles is strictly owned by `PerformanceTracker`.
- **Adaptive Feedback Loop**: Deterministic closed-loop adaptation: `Task -> Planner -> Scheduler -> Agent -> Execution -> Result -> Evaluation -> PerformanceTracker -> AgentProfile -> Scheduler`.
- **Fixed Scoring Policy**: In v0.5, ABOS adapts through updated `AgentProfile` data, NOT through self-modifying scheduler weights or reinforcement learning.
- **Framework Agnostic**: Pure Python standard library implementation without lock-in to FastAPI, LangGraph, LiteLLM, PostgreSQL, or Redis.
- **Result vs Evaluation Separation**: Agents produce Results; ABOS evaluates Results separately.

## Implemented vs Planned Architecture
- **IMPLEMENTED (v0.5 Pre-Release)**: Seven core domain contracts, three specialized agent implementations (`CalculatorAgent`, `TextAnalysisAgent`, `UnitConversionAgent`), Planner subsystem, Scheduler subsystem, Performance Tracker subsystem, Orchestrator, unit test suite (116 tests).
- **PLANNED**: Recovery system & Failure Handling (v0.6), Persistent Memory (v0.7), LangGraph orchestration (v0.8), LLM Planner & external integrations (Later).
