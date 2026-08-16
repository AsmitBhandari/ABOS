"""
ABOS v0.1: Core Foundation Prototype Entry Point
Demonstrates Task -> Orchestrator -> CalculatorAgent -> Result execution flow.
"""

from agents.calculator_agent import CalculatorAgent
from core.orchestrator import Orchestrator
from core.task import Task, TaskPriority


def main():
    print("=== ABOS v0.1: Core Foundation Prototype ===")
    print()

    # 1. Initialize Orchestrator and register Agents
    orchestrator = Orchestrator()
    calculator = CalculatorAgent()
    orchestrator.register_agent(calculator)

    # 2. Define a calculation Task
    expression = "25 * 37"
    task = Task(
        description=f"Calculate {expression}",
        input_data=expression,
        priority=TaskPriority.HIGH,
    )

    print(f"Task:\n  Description: {task.description}")
    print(f"  Input Data:  {task.input_data}")
    print(f"  Priority:    {task.priority.name}")
    print()

    # 3. Select agent via Orchestrator
    print("Orchestrator:")
    print("  Selecting suitable agent...")
    selected_agent = orchestrator.select_agent(task)
    if selected_agent:
        print(f"  Selected Agent: {selected_agent.name} (ID: {selected_agent.id})")
    else:
        print("  No suitable agent found!")
        return
    print()

    # 4. Execute Task through Orchestrator
    print("Executing task...")
    result = orchestrator.execute_task(task)
    print()

    # 5. Display Result
    print("Result:")
    print(f"  Success:  {result.success}")
    print(f"  Output:   {result.output}")
    print(f"  Agent ID: {result.agent_id}")
    print(f"  Error:    {result.error}")
    print()
    print(f"Status:\n  {task.status.value}")
    print()
    print("=== Execution Complete ===")


if __name__ == "__main__":
    main()
