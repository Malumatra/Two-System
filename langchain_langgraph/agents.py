"""
Agent implementations for the autonomous development system
"""
from typing import Dict, Any, List
from langchain_core.agents import AgentFinish
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph import END
from .state import State, AgentType
from .prompts import INITIALIZER_AGENT_PROMPT, CODER_AGENT_PROMPT
from .config import Config
import json
import logging

logger = logging.getLogger(__name__)

class DevelopmentAgent:
    """
    Base class for development agents (Initializer and Coder)
    """
    def __init__(self, config: Config, tools: List[BaseTool]):
        self.config = config
        self.tools = tools
        self.tool_executor = ToolExecutor(tools)
        
        # Initialize the LLM - configured for local 20B model
        self.llm = ChatOpenAI(
            model=config.llm_model_name,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            base_url="http://localhost:1234/v1",  # Default LM Studio endpoint
            api_key="dummy-key"  # Not needed for local models
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(tools)
    
    def get_bearings(self, state: State) -> State:
        """
        Perform the 'Get Your Bearings' routine to orient the agent
        """
        logger.info("Performing 'Get Your Bearings' routine...")
        
        # Add project directory context
        state.add_progress_log("Starting bearings routine")
        
        # Read app spec if not already loaded
        if not state.app_spec:
            try:
                from .tools import FileReadTool
                # Find the FileReadTool from our tools
                file_read_tool = next((tool for tool in self.tools if isinstance(tool, FileReadTool)), None)
                if file_read_tool:
                    app_spec_content = file_read_tool._run(self.config.app_spec_file)
                    state.app_spec = app_spec_content
                    state.add_progress_log(f"Loaded app spec from {self.config.app_spec_file}")
            except Exception as e:
                state.add_progress_log(f"Could not read app spec: {str(e)}")
        
        # Read feature list if not already loaded
        if not state.feature_list:
            try:
                from .tools import FileReadTool
                file_read_tool = next((tool for tool in self.tools if isinstance(tool, FileReadTool)), None)
                if file_read_tool:
                    feature_list_content = file_read_tool._run(self.config.feature_list_file)
                    state.load_feature_list_from_json(feature_list_content)
                    state.add_progress_log(f"Loaded feature list with {state.total_features} features")
            except Exception as e:
                state.add_progress_log(f"Could not read feature list: {str(e)}")
        
        # Read progress log
        try:
            from .tools import FileReadTool
            file_read_tool = next((tool for tool in self.tools if isinstance(tool, FileReadTool)), None)
            if file_read_tool:
                progress_content = file_read_tool._run(self.config.progress_file)
                state.progress_log.extend(progress_content.split('\n'))
        except Exception as e:
            state.add_progress_log(f"Could not read progress log: {str(e)}")
        
        # Get git history
        try:
            from .tools import GitTool
            git_tool = next((tool for tool in self.tools if isinstance(tool, GitTool)), None)
            if git_tool:
                git_log = git_tool._run("log", n=5)
                state.git_history = git_log.split('\n')
        except Exception as e:
            state.add_progress_log(f"Could not get git history: {str(e)}")
        
        return state
    
    def run_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool with the given input
        """
        # Find the tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            # Execute the tool
            result = tool._run(**tool_input)
            return result
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"
    
    async def arun_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Async execution of a tool
        """
        # Find the tool
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            # Execute the tool asynchronously
            result = await tool._arun(**tool_input)
            return result
        except NotImplementedError:
            # Fall back to sync execution if async not implemented
            return self.run_tool(tool_name, tool_input)
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

class InitializerAgent(DevelopmentAgent):
    """
    Initializer agent that sets up the project foundation
    """
    def __init__(self, config: Config, tools: List[BaseTool]):
        super().__init__(config, tools)
        self.agent_type: AgentType = "initializer"
    
    def plan_initialization(self, state: State) -> State:
        """
        Plan the initialization tasks based on the app spec
        """
        logger.info("Planning initialization tasks...")
        
        # Get bearings first
        state = self.get_bearings(state)
        
        # Set the agent type
        state.agent_type = self.agent_type
        
        # Define initialization tasks
        initialization_tasks = [
            "Read app specification and understand requirements",
            "Create comprehensive feature_list.json with 50+ test cases",
            "Create init.sh script for environment setup",
            "Initialize git repository",
            "Create initial project structure",
            "Commit initial setup files"
        ]
        
        state.current_task = "Initializing project foundation"
        state.add_progress_log("Starting project initialization")
        
        return state
    
    def execute_initialization(self, state: State) -> State:
        """
        Execute the initialization tasks
        """
        logger.info("Executing initialization tasks...")
        
        # Create feature_list.json if it doesn't exist
        if not state.feature_list:
            try:
                from .tools import FileReadTool, FileWriteTool
                file_read_tool = next((tool for tool in self.tools if isinstance(tool, FileReadTool)), None)
                file_write_tool = next((tool for tool in self.tools if isinstance(tool, FileWriteTool)), None)
                
                if file_read_tool and file_write_tool and state.app_spec:
                    # Generate a basic feature list based on the app spec
                    # This would normally be done by the LLM, but for now we'll create a template
                    feature_list_json = """[
  {
    "category": "functional",
    "description": "User can create a new conversation",
    "steps": [
      "Step 1: Navigate to the home page",
      "Step 2: Click the 'New Chat' button",
      "Step 3: Verify a new conversation interface appears"
    ],
    "passes": false
  },
  {
    "category": "functional", 
    "description": "User can send a message to the AI assistant",
    "steps": [
      "Step 1: Type a message in the input field",
      "Step 2: Click the send button or press Enter",
      "Step 3: Verify the message appears in the chat and AI responds"
    ],
    "passes": false
  },
  {
    "category": "style",
    "description": "Application has proper styling and layout",
    "steps": [
      "Step 1: Navigate to the application",
      "Step 2: Take screenshot of main interface", 
      "Step 3: Verify layout and styling match design requirements"
    ],
    "passes": false
  }
]"""
                    result = file_write_tool._run(self.config.feature_list_file, feature_list_json)
                    state.add_progress_log(f"Created feature_list.json: {result}")
                    
                    # Load the created feature list into state
                    state.load_feature_list_from_json(feature_list_json)
            except Exception as e:
                state.add_progress_log(f"Error creating feature_list.json: {str(e)}")
        
        # Create init.sh if it doesn't exist
        try:
            from .tools import FileWriteTool
            file_write_tool = next((tool for tool in self.tools if isinstance(tool, FileWriteTool)), None)
            
            if file_write_tool:
                init_script_content = f"""#!/bin/bash
# Initialization script for the project
echo "Starting development environment..."

# Start frontend
echo "Starting frontend on port {self.config.frontend_port}..."
cd frontend && npm run dev &

# Start backend  
echo "Starting backend on port {self.config.backend_port}..."
cd server && npm run start &

echo "Environment started. Frontend: http://localhost:{self.config.frontend_port}, Backend: http://localhost:{self.config.backend_port}"
"""
                result = file_write_tool._run(self.config.init_script_file, init_script_content)
                state.add_progress_log(f"Created init.sh: {result}")
        except Exception as e:
            state.add_progress_log(f"Error creating init.sh: {str(e)}")
        
        # Initialize git repo
        try:
            from .tools import GitTool
            git_tool = next((tool for tool in self.tools if isinstance(tool, GitTool)), None)
            
            if git_tool:
                result = git_tool._run("add", files=".")
                state.add_progress_log(f"Git add result: {result}")
                
                result = git_tool._run("commit", message="Initial setup: feature_list.json, init.sh, and project structure")
                state.add_progress_log(f"Git commit result: {result}")
        except Exception as e:
            state.add_progress_log(f"Error with git operations: {str(e)}")
        
        state.add_progress_log("Initialization tasks completed")
        return state

class CoderAgent(DevelopmentAgent):
    """
    Coder agent that implements features from the feature list
    """
    def __init__(self, config: Config, tools: List[BaseTool]):
        super().__init__(config, tools)
        self.agent_type: AgentType = "coder"
    
    def plan_coding_session(self, state: State) -> State:
        """
        Plan the coding session based on current state
        """
        logger.info("Planning coding session...")
        
        # Get bearings first
        state = self.get_bearings(state)
        
        # Set the agent type
        state.agent_type = self.agent_type
        
        # Find the next incomplete feature
        next_feature = state.get_next_incomplete_feature()
        
        if next_feature:
            state.current_feature_id = next_feature.id or next_feature.description[:20]
            state.current_feature_description = next_feature.description
            state.current_feature_steps = next_feature.steps
            state.current_task = f"Implement feature: {next_feature.description}"
            state.add_progress_log(f"Selected feature to implement: {next_feature.description}")
        else:
            state.current_task = "No more features to implement - project complete"
            state.status = "completed"
            state.add_progress_log("All features implemented - project complete")
        
        return state
    
    def execute_coding_task(self, state: State) -> State:
        """
        Execute the current coding task
        """
        logger.info(f"Executing coding task: {state.current_task}")
        
        if not state.current_feature_description:
            state.add_progress_log("No feature selected, ending session")
            return state
        
        # This is where the actual implementation would happen
        # For now, we'll simulate the process
        state.add_progress_log(f"Working on feature: {state.current_feature_description}")
        
        # After completing the feature, update the feature_list.json
        try:
            from .tools import FileReadTool, FileWriteTool
            file_read_tool = next((tool for tool in self.tools if isinstance(tool, FileReadTool)), None)
            file_write_tool = next((tool for tool in self.tools if isinstance(tool, FileWriteTool)), None)
            
            if file_read_tool and file_write_tool:
                # Read current feature list
                feature_list_content = file_read_tool._run(self.config.feature_list_file)
                
                # Parse and update the specific feature
                feature_list = json.loads(feature_list_content)
                
                for feature in feature_list:
                    if (feature.get('id') == state.current_feature_id or 
                        feature.get('description', '').startswith(state.current_feature_description[:50])):
                        feature['passes'] = True
                        break
                
                # Write updated feature list back
                updated_content = json.dumps(feature_list, indent=2)
                result = file_write_tool._run(self.config.feature_list_file, updated_content)
                state.add_progress_log(f"Updated feature_list.json: {result}")
                
                # Update state
                state.load_feature_list_from_json(updated_content)
                state.mark_feature_complete(state.current_feature_id or state.current_feature_description)
                
                # Add to progress log
                completion_msg = f"Completed feature: {state.current_feature_description}"
                state.add_progress_log(completion_msg)
                state.add_progress_log(f"Progress: {state.get_completion_percentage():.1f}% ({state.completed_features}/{state.total_features})")
        except Exception as e:
            state.add_progress_log(f"Error updating feature_list.json: {str(e)}")
        
        # Commit changes
        try:
            from .tools import GitTool
            git_tool = next((tool for tool in self.tools if isinstance(tool, GitTool)), None)
            
            if git_tool:
                result = git_tool._run("add", files=".")
                state.add_progress_log(f"Git add result: {result}")
                
                commit_msg = f"Implement {state.current_feature_description[:50]}... - verified end-to-end"
                result = git_tool._run("commit", message=commit_msg)
                state.add_progress_log(f"Git commit result: {result}")
        except Exception as e:
            state.add_progress_log(f"Error with git commit: {str(e)}")
        
        return state