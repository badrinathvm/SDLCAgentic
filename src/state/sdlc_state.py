from pydantic import BaseModel, Field
from typing import TypedDict, Any, Dict, Literal, Optional
import json

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

class DesignDocument(BaseModel):
    functional: str = Field(..., description="Holds the functional design Document")
    technical: str = Field(..., description="Holds the technical design Document")
    review_status: str = Field("", description="Indicates whether the design document has been reviwed")
    feedback_reason: str = Field("", description="Holds the design feedback")

class SDLCState(TypedDict):
    project_name: str
    task: str
    requirements: list[str]
    user_stories: list[UserStories]
    progress: int
    next_required_input: Optional[str]
    current_node: str = "project_initilization"
    status: Literal["initialized", "in_progress", "completed", "error"] = "initialized"
    product_decision: str
    feedback_reason: str
    design_documents: DesignDocument
    code_generated: str
    code_review_comments: str
    code_review_status: str
    security_review_comments: str
    security_review_status: str
    security_review_feedback: str
    test_cases: str
    test_case_review_status: str
    test_case_review_feedback: str
    qa_testing_status: str
    qa_testing_comments: str
    qa_testing_feedback: str
    deployment_status: str
    deployment_feedback: str

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        # Check if the object is any kind of Pydantic model
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # Or check for specific classes if needed
        # if isinstance(obj, UserStories) or isinstance(obj, DesignDocument):
        #     return obj.model_dump()
        return super().default(obj)