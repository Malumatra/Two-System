"""
Tools for the autonomous development system
These tools will be available to both initializer and coder agents
"""
import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import git
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from config import Config

class FileReadTool(BaseTool):
    """Tool to read file contents"""
    name = "file_read"
    description = "Read the contents of a file"
    config: Config = Field(default_factory=Config)
    
    def _run(self, filepath: str) -> str:
        """Read a file's contents"""
        try:
            full_path = os.path.join(self.config.project_dir, filepath)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"File not found: {filepath}"
        except Exception as e:
            return f"Error reading file {filepath}: {str(e)}"
    
    async def _arun(self, filepath: str):
        raise NotImplementedError("FileReadTool does not support async")

class FileWriteTool(BaseTool):
    """Tool to write content to a file"""
    name = "file_write"
    description = "Write content to a file, creating directories if needed"
    config: Config = Field(default_factory=Config)
    
    def _run(self, filepath: str, content: str) -> str:
        """Write content to a file"""
        try:
            full_path = os.path.join(self.config.project_dir, filepath)
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing file {filepath}: {str(e)}"
    
    async def _arun(self, filepath: str, content: str):
        raise NotImplementedError("FileWriteTool does not support async")

class BashTool(BaseTool):
    """Tool to execute bash commands"""
    name = "bash_command"
    description = "Execute a bash command in the project directory"
    config: Config = Field(default_factory=Config)
    
    def _run(self, command: str) -> str:
        """Execute a bash command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.config.project_dir,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            if result.returncode != 0:
                output += f"\nEXIT CODE: {result.returncode}"
            return output
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    async def _arun(self, command: str):
        raise NotImplementedError("BashTool does not support async")

class GitTool(BaseTool):
    """Tool to interact with git"""
    name = "git_command"
    description = "Execute git operations in the project directory"
    config: Config = Field(default_factory=Config)
    
    def _run(self, operation: str, **kwargs) -> str:
        """Perform git operations"""
        try:
            repo_path = self.config.project_dir
            # Initialize git repo if it doesn't exist
            if not os.path.exists(os.path.join(repo_path, '.git')):
                git.Repo.init(repo_path)
            
            repo = git.Repo(repo_path)
            
            if operation == "status":
                return repo.git.status()
            elif operation == "log":
                n = kwargs.get("n", 10)
                return repo.git.log("--oneline", f"-{n}")
            elif operation == "add":
                files = kwargs.get("files", ".")
                repo.git.add(files)
                return f"Added {files} to staging"
            elif operation == "commit":
                message = kwargs.get("message", "Auto-commit")
                repo.git.commit("-m", message)
                return f"Committed with message: {message}"
            elif operation == "diff":
                return repo.git.diff()
            else:
                return f"Unknown git operation: {operation}"
        except Exception as e:
            return f"Git operation failed: {str(e)}"
    
    async def _arun(self, operation: str, **kwargs):
        raise NotImplementedError("GitTool does not support async")

class PuppeteerNavigateTool(BaseTool):
    """Tool to navigate to a URL with puppeteer (for testing)"""
    name = "puppeteer_navigate"
    description = "Navigate to a URL with a headless browser for testing"
    config: Config = Field(default_factory=Config)
    
    def _run(self, url: str) -> str:
        """Navigate to URL and return page info"""
        # In a real implementation, this would use puppeteer
        # For now, we'll simulate the functionality
        return f"Navigated to {url}. This would normally return page content for testing."
    
    async def _arun(self, url: str):
        raise NotImplementedError("PuppeteerNavigateTool does not support async")

class PuppeteerScreenshotTool(BaseTool):
    """Tool to take a screenshot with puppeteer"""
    name = "puppeteer_screenshot"
    description = "Take a screenshot of the current page and save to file"
    config: Config = Field(default_factory=Config)
    
    def _run(self, filename: str) -> str:
        """Take a screenshot"""
        # In a real implementation, this would use puppeteer
        # For now, we'll simulate the functionality
        screenshot_path = os.path.join(self.config.screenshot_dir, filename)
        os.makedirs(self.config.screenshot_dir, exist_ok=True)
        # This would actually take a screenshot in a real implementation
        return f"Screenshot saved to {screenshot_path} (simulated)"
    
    async def _arun(self, filename: str):
        raise NotImplementedError("PuppeteerScreenshotTool does not support async")

class PuppeteerClickTool(BaseTool):
    """Tool to click an element with puppeteer"""
    name = "puppeteer_click"
    description = "Click an element on the page identified by selector"
    config: Config = Field(default_factory=Config)
    
    def _run(self, selector: str) -> str:
        """Click an element"""
        # In a real implementation, this would use puppeteer
        # For now, we'll simulate the functionality
        return f"Clicked element with selector: {selector} (simulated)"
    
    async def _arun(self, selector: str):
        raise NotImplementedError("PuppeteerClickTool does not support async")

class PuppeteerFillTool(BaseTool):
    """Tool to fill an input field with puppeteer"""
    name = "puppeteer_fill"
    description = "Fill an input field identified by selector with text"
    config: Config = Field(default_factory=Config)
    
    def _run(self, selector: str, text: str) -> str:
        """Fill an input field"""
        # In a real implementation, this would use puppeteer
        # For now, we'll simulate the functionality
        return f"Filled {selector} with '{text}' (simulated)"
    
    async def _arun(self, selector: str, text: str):
        raise NotImplementedError("PuppeteerFillTool does not support async")

def get_all_tools(config: Config) -> List[BaseTool]:
    """Get all tools for the agents"""
    return [
        FileReadTool(config=config),
        FileWriteTool(config=config),
        BashTool(config=config),
        GitTool(config=config),
        PuppeteerNavigateTool(config=config),
        PuppeteerScreenshotTool(config=config),
        PuppeteerClickTool(config=config),
        PuppeteerFillTool(config=config),
    ]