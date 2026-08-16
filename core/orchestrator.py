from typing import Dict, List, Optional
from core.agent import AgentState, BaseAgent
from core.result import Result
from core.task import Task, TaskStatus


class Orchestrator:
    """Coordinates Task assignment, Agent selection, and Result routing."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.id] = agent

    def select_agent(self, task: Task, required_capability: Optional[str] = None) -> Optional[BaseAgent]:
        """
        Select an appropriate agent for the task based on capability matching.
        If required_capability is not specified, inspects task description or input.
        """
        target_cap = required_capability
        if not target_cap:
            desc_lower = (task.description or "").lower()
            if "calculate" in desc_lower or "math" in desc_lower or "eval" in desc_lower:
                target_cap = "math"

        for agent in self.agents.values():
            if target_cap and target_cap in agent.capabilities:
                return agent

        # Fallback: return the first idle agent if no specific capability match
        for agent in self.agents.values():
            if agent.state == AgentState.IDLE:
                return agent

        return None

    def execute_task(self, task: Task, required_capability: Optional[str] = None) -> Result:
        """
        Route task to suitable agent, manage lifecycle, and return structured Result.
        """
        agent = self.select_agent(task, required_capability=required_capability)
        if not agent:
            error_msg = f"No suitable agent found for task: {task.description}"
            res = Result(
                success=False,
                error=error_msg,
                agent_id="Orchestrator",
                metadata={"task_id": task.id}
            )
            task.status = TaskStatus.FAILED
            task.result = res
            return res

        task.status = TaskStatus.IN_PROGRESS
        agent.state = AgentState.BUSY
        try:
            result = agent.execute(task)
            task.result = result
            if result.success:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
            return result
        except Exception as e:
            error_res = Result(
                success=False,
                error=f"Unhandled exception during agent execution: {str(e)}",
                agent_id=agent.id,
                metadata={"task_id": task.id, "exception_type": type(e).__name__}
            )
            task.status = TaskStatus.FAILED
            task.result = error_res
            return error_res
        finally:
            agent.state = AgentState.IDLE
