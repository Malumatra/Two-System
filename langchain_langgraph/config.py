"""
Configuration for the Langgraph-based autonomous development system
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration for the autonomous development system"""
    
    # LLM Configuration - Optimized for 20B parameter local model
    llm_model_name: str = "local-20b-model"  # Placeholder for local model
    llm_temperature: float = 0.1  # Lower temperature for more consistent outputs
    llm_max_tokens: int = 2048
    llm_context_window: int = 8192  # Context window for the 20B model
    
    # File paths and state management
    project_dir: str = "./project"
    app_spec_file: str = "app_spec.txt"
    feature_list_file: str = "feature_list.json"
    progress_file: str = "claude-progress.txt"
    init_script_file: str = "init.sh"
    git_repo_file: str = ".git"
    
    # Agent configuration
    max_attempts_per_feature: int = 50  # Prevent infinite loops
    max_session_tokens: int = 4000  # Reserve context for system messages
    
    # Development environment
    frontend_port: int = 3000
    backend_port: int = 8000
    
    # Browser automation (for testing)
    browser_headless: bool = True
    screenshot_dir: str = "screenshots"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls(
            llm_model_name=os.getenv('LLM_MODEL_NAME', 'local-20b-model'),
            llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.1')),
            llm_max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2048')),
            llm_context_window=int(os.getenv('LLM_CONTEXT_WINDOW', '8192')),
            project_dir=os.getenv('PROJECT_DIR', './project'),
            frontend_port=int(os.getenv('FRONTEND_PORT', '3000')),
            backend_port=int(os.getenv('BACKEND_PORT', '8000')),
            max_attempts_per_feature=int(os.getenv('MAX_ATTEMPTS_PER_FEATURE', '50')),
        )