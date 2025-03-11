
import asyncio
from src.state.sdlc_state import SDLCState, UserStories
from langchain_core.messages import SystemMessage


class SDLCNode:
    def __init__(self, llm):
        self.llm = llm 

    
    def project_initilization(self, state: SDLCState):
        """
            Performs the project initilazation
        """
        # TODO: We need to calculate how many steps int he life cycle as of now harcoded to 10
        state['progress'] = 10
        state['status'] = "in_progress"
        state['next_required_input'] = "requirements"
        state['current_node'] = 'project_initilization'
        return state
    
    def get_requirements(self, state: SDLCState):
        """
            Gets the requirements from the user
        """
        pass

    async def generate_user_story(self, project_name: str, requirement: str, index: int) -> UserStories:
        prompt = f"""
        You are an expert in software development and requirements analysis. Based on the project name "{project_name}" and the following requirement:
        - {requirement}
        
        Please generate a user story in Markdown format. The user story should include:
        - A unique identifier: {index}
        - A title
        - A detailed description
        - The current status (e.g., "To Do")

        Format the user story as a bullet point.
        """
        system_message = prompt.format(project_name= project_name, requirement= requirement, index= index)
        llm_with_structured = self.llm.with_structured_output(UserStories)
        response = llm_with_structured.invoke(system_message)
        return response


    async def auto_generate_user_stories(self, state: SDLCState):
        """
            Auto generate the user stories based on the user requirements provided
        """
        project_name = state["project_name"]
        requirements = state["requirements"]

        tasks = [
            self.generate_user_story(project_name, requirement, index)
            for index, requirement in enumerate(requirements, start=1)
        ]

        user_stories = await asyncio.gather(*tasks)
        return {"user_stories": user_stories}


    
