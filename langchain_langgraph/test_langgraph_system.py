import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

# Import all the components we need to test
from langchain_langgraph.config import Config
from langchain_langgraph.state import State
from langchain_langgraph.tools import (
    FileReadTool,
    FileWriteTool,
    BashTool,
    GitTool,
    PuppeteerNavigateTool,
    get_all_tools
)
from langchain_langgraph.agents import InitializerAgent, CoderAgent
from langchain_langgraph.workflow import create_initial_state, run_autonomous_development
from langchain_langgraph.prompts import (
    INITIALIZER_AGENT_PROMPT,
    CODER_AGENT_PROMPT
)


class TestConfig(unittest.TestCase):
    """Test configuration system"""
    
    def test_config_initialization(self):
        """Test that Config is properly initialized with 20B model settings"""
        config = Config()
        self.assertIsNotNone(config)
        self.assertEqual(config.temperature, 0.1)
        self.assertEqual(config.max_tokens, 2048)
        self.assertEqual(config.model_name, "local-20b-model")
        self.assertEqual(config.context_window, 8192)


class TestState(unittest.TestCase):
    """Test state management"""
    
    def test_code_state_initialization(self):
        """Test State initialization"""
        from langchain_langgraph.state import AgentType
        state = State(
            agent_type="initializer",
            project_dir="/tmp/test_project",
            app_spec="Test specification",
            current_task="Test task",
            completed_features=0,
            total_features=5,
            max_attempts=50
        )
        
        self.assertEqual(state.project_dir, "/tmp/test_project")
        self.assertEqual(state.app_spec, "Test specification")
        self.assertEqual(state.current_task, "Test task")
        self.assertEqual(state.completed_features, 0)
        self.assertEqual(state.total_features, 5)
        self.assertEqual(state.max_attempts, 50)


class TestFileTools(unittest.TestCase):
    """Test file operation tools"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create a config object for the tools
        self.config = Config()
        self.config.project_dir = self.test_dir
        
    def tearDown(self):
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_file_read_tool(self):
        """Test FileReadTool"""
        # Create a test file
        test_file_path = os.path.join(self.test_dir, "test.txt")
        test_content = "Hello, World!"
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        # Test the tool
        tool = FileReadTool(config=self.config)
        result = tool._run("test.txt")
        
        self.assertEqual(result, test_content)
    
    def test_file_write_tool(self):
        """Test FileWriteTool"""
        tool = FileWriteTool(config=self.config)
        content = "Hello, World!"
        result = tool._run("test.txt", content)
        
        self.assertTrue("Successfully wrote to" in result)
        
        # Verify the file was created with correct content
        file_path = os.path.join(self.test_dir, "test.txt")
        self.assertTrue(os.path.exists(file_path))
        
        with open(file_path, 'r') as f:
            saved_content = f.read()
        self.assertEqual(saved_content, content)


class TestBashCommand(unittest.TestCase):
    """Test bash command execution"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.project_dir = self.test_dir
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_bash_tool_success(self):
        """Test executing a successful bash command"""
        tool = BashTool(config=self.config)
        result = tool._run("echo 'Hello World'")
        self.assertTrue("Hello World" in result)
    
    def test_bash_tool_failure(self):
        """Test executing a failing bash command"""
        tool = BashTool(config=self.config)
        result = tool._run("ls /nonexistent/directory")
        self.assertTrue("No such file or directory" in result or "cannot access" in result.lower())


class TestGitCommand(unittest.TestCase):
    """Test git command execution"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.project_dir = self.test_dir
        # Initialize a git repo in the test directory
        os.system(f"cd {self.test_dir} && git init > /dev/null 2>&1")
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_git_tool_status(self):
        """Test git status command"""
        tool = GitTool(config=self.config)
        result = tool._run("status")
        # Should return status info
        self.assertIsNotNone(result)
        self.assertIn("On branch", result)
    
    def test_git_tool_log(self):
        """Test git log command"""
        tool = GitTool(config=self.config)
        result = tool._run("log", n=5)
        # Should return log or empty if no commits
        self.assertIsNotNone(result)


class TestBrowserAutomation(unittest.TestCase):
    """Test browser automation tool"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.project_dir = self.test_dir
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_puppeteer_navigate_tool(self):
        """Test puppeteer navigate tool"""
        tool = PuppeteerNavigateTool(config=self.config)
        result = tool._run("https://example.com")
        self.assertTrue("Navigated to https://example.com" in result)





class TestWorkflow(unittest.TestCase):
    """Test workflow creation"""
    
    def test_create_workflow(self):
        """Test workflow creation"""
        workflow = create_workflow()
        
        # Check that workflow has the expected nodes
        nodes = workflow.get_graph().nodes
        self.assertIn("initializer", nodes)
        self.assertIn("coder", nodes)
        self.assertIn("get_your_bearings", nodes)
        
        # Check that workflow has the expected edges
        edges = workflow.get_graph().edges
        self.assertTrue(len(edges) > 0)


class TestPrompts(unittest.TestCase):
    """Test prompt templates"""
    
    def test_prompts_exist(self):
        """Test that all required prompts exist"""
        self.assertIsInstance(INITIALIZER_PROMPT, str)
        self.assertIsInstance(CODER_PROMPT, str)
        self.assertIsInstance(GET_YOUR_BEARINGS_PROMPT, str)
        
        # Check that prompts contain expected placeholders
        self.assertTrue("{specification}" in INITIALIZER_PROMPT)
        self.assertTrue("{current_feature}" in CODER_PROMPT)
        self.assertTrue("{project_dir}" in GET_YOUR_BEARINGS_PROMPT)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test a basic workflow execution"""
        # This is a high-level test that verifies the components can work together
        state = CodeState(
            project_dir=self.test_dir,
            specification="Test specification",
            feature_list=["test_feature"],
            current_feature="test_feature",
            code_files=[],
            terminal_output="",
            messages=["Start test"],
            completed_features=[],
            error_count=0,
            max_errors=5
        )
        
        # Verify state was created correctly
        self.assertEqual(state.project_dir, self.test_dir)
        self.assertEqual(state.specification, "Test specification")
        self.assertEqual(len(state.feature_list), 1)


class TestAgents(unittest.TestCase):
    """Test agent classes"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config = Config()
        self.config.project_dir = self.test_dir
        
        # Create some tools for the agents
        from langchain_langgraph.tools import get_all_tools
        self.tools = get_all_tools(self.config)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initializer_agent_creation(self):
        """Test InitializerAgent creation"""
        agent = InitializerAgent(self.config, self.tools)
        
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_type, "initializer")
        self.assertEqual(len(agent.tools), len(self.tools))
    
    def test_coder_agent_creation(self):
        """Test CoderAgent creation"""
        agent = CoderAgent(self.config, self.tools)
        
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_type, "coder")
        self.assertEqual(len(agent.tools), len(self.tools))
    
    def test_initializer_agent_methods(self):
        """Test InitializerAgent methods"""
        agent = InitializerAgent(self.config, self.tools)
        
        # Create a state
        state = State(agent_type="initializer")
        state.project_dir = self.test_dir
        
        # Test plan_initialization method
        updated_state = agent.plan_initialization(state)
        self.assertEqual(updated_state.agent_type, "initializer")
        self.assertIsNotNone(updated_state.current_task)
        
        # Test execute_initialization method
        final_state = agent.execute_initialization(updated_state)
        self.assertIsNotNone(final_state)
    
    def test_coder_agent_methods(self):
        """Test CoderAgent methods"""
        agent = CoderAgent(self.config, self.tools)
        
        # Create a state
        state = State(agent_type="coder")
        state.project_dir = self.test_dir
        
        # Test plan_coding_session method
        updated_state = agent.plan_coding_session(state)
        self.assertEqual(updated_state.agent_type, "coder")
        
        # Test execute_coding_task method
        final_state = agent.execute_coding_task(updated_state)
        self.assertIsNotNone(final_state)


class TestWorkflow(unittest.TestCase):
    """Test workflow creation"""
    
    def test_create_initial_state(self):
        """Test create_initial_state function"""
        state = create_initial_state(agent_type="initializer", project_dir="/tmp/test")
        
        self.assertIsNotNone(state)
        self.assertEqual(state.agent_type, "initializer")
        self.assertEqual(state.project_dir, "/tmp/test")
    
    def test_run_autonomous_development(self):
        """Test run_autonomous_development function"""
        # This is a basic test to ensure the function can be called
        config = Config()
        config.project_dir = tempfile.mkdtemp()
        
        # We can't fully test this function without mocking the LLM,
        # but we can test that it exists and can be called
        try:
            # Since this function runs the full workflow, we'll just check it exists
            self.assertIsNotNone(run_autonomous_development)
        except Exception:
            # Expected if there are unmet dependencies
            pass


class TestPrompts(unittest.TestCase):
    """Test prompt templates"""
    
    def test_prompts_exist(self):
        """Test that all required prompts exist"""
        self.assertIsInstance(INITIALIZER_AGENT_PROMPT, str)
        self.assertIsInstance(CODER_AGENT_PROMPT, str)
        
        # Check that prompts contain expected placeholders
        self.assertTrue("{app_spec}" in INITIALIZER_AGENT_PROMPT or "{specification}" in INITIALIZER_AGENT_PROMPT)
        self.assertTrue("{current_feature}" in CODER_AGENT_PROMPT or "{feature_description}" in CODER_AGENT_PROMPT)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_tool_set(self):
        """Test that all tools can be created together"""
        config = Config()
        config.project_dir = self.test_dir
        
        # Get all tools
        tools = get_all_tools(config)
        
        # Verify we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "file_read", "file_write", "bash_command", 
            "git_command", "puppeteer_navigate", 
            "puppeteer_screenshot", "puppeteer_click", 
            "puppeteer_fill"
        ]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names)
        
        self.assertEqual(len(tools), len(expected_tools))


if __name__ == "__main__":
    print("Running Langgraph System Tests...")
    print("=" * 50)
    
    # Run all tests
    unittest.main(verbosity=2)