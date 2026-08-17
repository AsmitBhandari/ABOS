# ABOS Permanent Engineering Rules

## General Rules
* Keep the architecture modular.
* Prefer simple solutions over unnecessary abstraction.
* Use clear naming.
* Use type hints for all signatures and fields.
* Keep classes and functions focused and single-purpose.
* Avoid unnecessary dependencies; prefer standard library where sufficient.
* Avoid unnecessary global state.
* Do not silently change existing behavior.

## Core Domain Independence Rule (Mandatory)
> **Core objects must contain domain information, not infrastructure concerns.**

Core domain objects must represent ABOS concepts independently of infrastructure and external frameworks.

Core objects must NOT directly depend on:
- FastAPI request/response objects
- LangGraph state
- LangChain
- LiteLLM
- LLM clients
- PostgreSQL sessions
- SQLAlchemy sessions
- Redis clients
- Celery tasks
- HTTP clients
- database connections
- framework-specific runtime objects

Infrastructure-specific behavior belongs in:
- orchestration
- services
- adapters
- infrastructure
- runtime integrations

The domain layer must remain usable without any external framework.
This rule applies to all future ABOS development.

## Architecture Rules
* Tasks must remain independent of specific agents.
* Agents must follow a common `BaseAgent` contract.
* Tools must remain independent of individual agents.
* Results must use the common `Result` structure.
* The Orchestrator coordinates agents rather than containing agent-specific implementation logic.
* `main.py` should remain a thin application entry point.
* Core business logic must not be placed inside `main.py`.
* Runtime memory (`memory/`) must remain separate from development context (`context/`).

## Security Rules
* Never commit API keys, passwords, or credentials.
* Never expose secrets in log outputs or metadata.
* Never create unnecessary external services or listening sockets.
* Never hard-code machine-specific paths or usernames.
* Never use unsafe code execution such as direct `eval()` on untrusted string expressions.

## Development Discipline
* Work only within the current milestone (v0.2).
* Do not implement future features prematurely (e.g. LLM integration, databases, cloud features).
* Do not add an LLM merely because it is available.
* Do not add external frameworks without a clear, documented reason.
* Do not replace simple deterministic functionality with AI unnecessarily.
* Keep changes small, clean, and reviewable.
* Update tests whenever behavior changes.
