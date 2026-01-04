"""
LangGraph workflow for the autonomous development system
Implements the two-agent system (Initializer and Coder) with proper state management
"""
from typing import Dict, Literal, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from .state import State
from .agents import InitializerAgent, CoderAgent
from .tools import get_all_tools
from .config import Config
import logging

logger = logging.getLogger(__name__)

class DevelopmentWorkflow:
    """
    LangGraph workflow for the autonomous development system
    """
    def __init__(self, config: Config):
        self.config = config
        self.tools = get_all_tools(config)
        self.tool_executor = ToolExecutor(self.tools)
        
        # Create agents
        self.initializer_agent = InitializerAgent(config, self.tools)
        self.coder_agent = CoderAgent(config, self.tools)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine
        """
        # Create state graph
        workflow = StateGraph(State)
        
        # Add nodes for each agent action
        workflow.add_node("initializer_plan", self.initializer_agent.plan_initialization)
        workflow.add_node("initializer_execute", self.initializer_agent.execute_initialization)
        workflow.add_node("coder_plan", self.coder_agent.plan_coding_session)
        workflow.add_node("coder_execute", self.coder_agent.execute_coding_task)
        
        # Set entry point
        workflow.set_entry_point("initializer_plan")
        
        # Define transitions
        # Initializer transitions
        workflow.add_edge("initializer_plan", "initializer_execute")
        workflow.add_edge("initializer_execute", "coder_plan")
        
        # Coder transitions
        workflow.add_edge("coder_plan", "coder_execute")
        
        # Conditional edge from coder_execute back to itself or to end
        workflow.add_conditional_edges(
            "coder_execute",
            self._should_continue,
            {
                "continue": "coder_plan",  # Continue coding if more features
                "end": END  # End if all features are complete
            }
        )
        
        return workflow.compile()
    
    def _should_continue(self, state: State) -> Literal["continue", "end"]:
        """
        Determine if the workflow should continue or end
        """
        # Check if all features are completed
        if state.status == "completed":
            logger.info("All features completed, ending workflow")
            return "end"
        
        # Check attempt count to prevent infinite loops
        if state.attempt_count >= state.max_attempts:
            logger.info(f"Max attempts ({state.max_attempts}) reached, ending workflow")
            state.status = "stopped"
            return "end"
        
        # Check if there are more incomplete features
        next_feature = state.get_next_incomplete_feature()
        if next_feature is None:
            logger.info("No more incomplete features, ending workflow")
            state.status = "completed"
            return "end"
        
        # Increment attempt count
        state.attempt_count += 1
        
        logger.info(f"Continuing workflow, attempt {state.attempt_count}/{state.max_attempts}")
        return "continue"
    
    def run(self, initial_state: State) -> State:
        """
        Run the development workflow
        """
        logger.info("Starting development workflow")
        
        # Execute the workflow
        final_state = self.graph.invoke(initial_state)
        
        logger.info("Development workflow completed")
        return final_state

def create_initial_state(agent_type: str = "initializer", project_dir: str = "./project") -> State:
    """
    Create an initial state for the workflow
    """
    from datetime import datetime
    
    return State(
        agent_type=agent_type,
        project_dir=project_dir,
        session_start_time=datetime.now(),
        max_attempts=50,
        status="running"
    )

# Example usage function
def run_autonomous_development(config: Config = None):
    """
    Run the complete autonomous development process
    """
    if config is None:
        config = Config()
    
    # Create initial state
    initial_state = create_initial_state("initializer", config.project_dir)
    
    # Create and run workflow
    workflow = DevelopmentWorkflow(config)
    final_state = workflow.run(initial_state)
    
    return final_state

if __name__ == "__main__":
    # Example of how to run the workflow
    import os
    
    # Create config
    config = Config.from_env()
    
    # Make sure project directory exists
    os.makedirs(config.project_dir, exist_ok=True)
    
    # Run the workflow
    final_state = run_autonomous_development(config)
    
    print(f"Workflow completed with status: {final_state.status}")
    print(f"Completed {final_state.completed_features}/{final_state.total_features} features")
    print(f"Progress: {final_state.get_completion_percentage():.1f}%")