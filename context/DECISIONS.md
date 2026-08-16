# Architectural Decisions Log

## Decision 1: Agent must remain LLM-independent

**Date**: 2026-08-16

**Decision**:
The base `Agent` abstraction must not depend directly on an LLM provider or external framework.

**Reason**:
ABOS must support deterministic agents, ML agents, rule-based agents, and LLM agents under a unified interface.

**Alternatives Considered**:
- Use LangChain/CrewAI base classes.
- Assume all agents take natural language prompts and return text via LLM APIs.

**Consequences**:
The `BaseAgent` interface remains generic, lightweight, and framework-independent.

---

## Decision 2: Safe AST parsing for mathematical evaluation

**Date**: 2026-08-16

**Decision**:
`CalculatorAgent` must parse and evaluate arithmetic expressions using standard Python AST node traversal rather than `eval()`.

**Reason**:
Passing raw strings to `eval()` allows arbitrary code execution (e.g. `__import__('os').system(...)`), creating a severe security vulnerability.

**Alternatives Considered**:
- Direct `eval()`.
- External math parsing libraries (`sympy`, `numexpr`).

**Consequences**:
Maintains strict security without adding external dependencies.

---

## Decision 3: Standardized Result object across all execution flows

**Date**: 2026-08-16

**Decision**:
Every agent execution must return a `Result` dataclass containing `success`, `output`, `error`, `agent_id`, and `metadata`.

**Reason**:
Guarantees consistent error handling and outcome reporting throughout the orchestrator and caller pipeline without unstructured runtime exceptions.

**Alternatives Considered**:
- Throwing exceptions directly to the orchestrator.
- Returning raw values or tuples.

**Consequences**:
Execution failures are captured safely in a structured, serializable format.
