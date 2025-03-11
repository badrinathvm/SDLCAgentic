from pydantic import BaseModel, Field
from typing import TypedDict

class UserStories(BaseModel):
    id: int = Field(..., description="The unique identifier of the user story")
    title: str = Field(..., description="The title of the user story")
    description: str = Field(..., description="A detailed explanation of the user story")
    status: str = Field(..., description="The current status of the user story", examples="To Do")


class SDLCState(TypedDict):
    project_name: str
    requirements: list[str]
    user_stories: list[UserStories]