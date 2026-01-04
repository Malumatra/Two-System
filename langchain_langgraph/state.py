"""
State management for the autonomous development system
"""
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
import json

# Define the possible agent types
AgentType = Literal["initializer", "coder"]

@dataclass
class Feature:
    """Represents a single feature/test in the feature list"""
    category: str  # e.g., "functional", "style"
    description: str
    steps: List[str]
    passes: bool = False
    id: Optional[str] = None

@dataclass
class State:
    """
    State for the autonomous development system
    This state is managed by LangGraph to maintain context between agent calls
    """
    # Agent identification
    agent_type: AgentType
    session_id: str = ""
    
    # Project state
    project_dir: str = "./project"
    app_spec: str = ""
    feature_list: List[Feature] = field(default_factory=list)
    progress_log: List[str] = field(default_factory=list)
    git_history: List[str] = field(default_factory=list)
    
    # Current session state
    current_task: str = ""
    current_feature_id: Optional[str] = None
    current_feature_description: str = ""
    current_feature_steps: List[str] = field(default_factory=list)
    verification_results: Dict[str, Any] = field(default_factory=dict)
    
    # System state
    completed_features: int = 0
    total_features: int = 0
    session_start_time: datetime = field(default_factory=datetime.now)
    attempt_count: int = 0
    max_attempts: int = 50
    
    # Files and artifacts
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    screenshots_taken: List[str] = field(default_factory=list)
    
    # Error and status tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    status: str = "running"  # running, completed, error, stopped
    
    def load_feature_list_from_json(self, json_content: str):
        """Load feature list from JSON string"""
        try:
            data = json.loads(json_content)
            self.feature_list = [Feature(**feature_dict) for feature_dict in data]
            self.total_features = len(self.feature_list)
            self.completed_features = sum(1 for f in self.feature_list if f.passes)
        except json.JSONDecodeError as e:
            self.errors.append(f"Failed to parse feature_list.json: {str(e)}")
        except Exception as e:
            self.errors.append(f"Error loading feature list: {str(e)}")
    
    def get_next_incomplete_feature(self) -> Optional[Feature]:
        """Get the next feature that hasn't been completed yet"""
        for feature in self.feature_list:
            if not feature.passes:
                return feature
        return None
    
    def mark_feature_complete(self, feature_id: str):
        """Mark a specific feature as complete"""
        for feature in self.feature_list:
            if feature.id == feature_id or feature.description.startswith(feature_id[:50]):  # Partial match for ID
                feature.passes = True
                self.completed_features += 1
                break
    
    def add_progress_log(self, message: str):
        """Add a message to the progress log"""
        timestamp = datetime.now().isoformat()
        self.progress_log.append(f"[{timestamp}] {message}")
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of completed features"""
        if self.total_features == 0:
            return 0.0
        return (self.completed_features / self.total_features) * 100.0