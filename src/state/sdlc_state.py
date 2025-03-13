from pydantic import BaseModel, Field
from typing import TypedDict, Any, Dict, Literal, Optional

class UserStories(BaseModel):
    id: int = Field(..., description="The unique identifier of the user story")
    title: str = Field(..., description="The title of the user story")
    description: str = Field(..., description="A detailed explanation of the user story")
    status: str = Field(..., description="The current status of the user story", examples="To Do")

class StartWorkflowRequest(BaseModel):
    project_name: str
    #initial_context: Optional[Dict[str, Any]]

class StartWorkflowResponse(BaseModel):
    task_id: str
    status: str
    next_required_input: Optional[str]
    progress: int
    current_node: str

class SDLCState(TypedDict):
    project_name: str
    requirements: list[str]
    user_stories: list[UserStories]
    progress: int
    next_required_input: Optional[str]
    current_node: str = "project_initilization"
    status: Literal["initialized", "in_progress", "completed", "error"] = "initialized"
    product_decision: str
    feedback_reasons: list[str]