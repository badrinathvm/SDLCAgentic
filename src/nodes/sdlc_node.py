
import asyncio
from typing import Literal
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

    async def generate_user_story(self, project_name: str, requirement: str, feedback_reason: str, index: int) -> UserStories:
        prompt = f"""
        You are an expert in software development and requirements analysis. Based on the project name "{project_name}" and the following requirement:
        - {requirement}

        Please generate a user story in Markdown format. The user story should include:
        - A unique identifier: {index}
        - A title
        - A detailed description
        - The current status (e.g., "To Do")

        {f"When creating this user story, please incorporate the following feedback about the requirements: {feedback_reason}" if feedback_reason else ""}

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
        print("----- Generate User Stories ----")
        project_name = state["project_name"]
        requirements = state["requirements"]
        if 'feedback_reason' in state:
            feedback_reason = state["feedback_reason"]
            #next_required_input = 'product_owner_review'
        else:
            feedback_reason = ''
            next_required_input = 'product_owner_review'

        tasks = [
            self.generate_user_story(project_name, requirement, feedback_reason, index)
            for index, requirement in enumerate(requirements, start=1)
        ]

        user_stories = await asyncio.gather(*tasks)
        return {"user_stories": user_stories, 'next_required_input': 'product_owner_review', 'current_node': 'auto_generate_user_stories'}
    
    def product_owner_review_decision(self, state: SDLCState):
        """
            Reviews the product requirements and returns the decision in state
        """
        product_owner_decision = state['product_decision']
        return state
    
  
    def product_decision_router(self, state: SDLCState):
        """
            Router function for product review decision
        """
        state['current_node'] = 'product_owner_decision'
        return state["product_decision"]

    
    # def product_owner_review_decision1(self, state: SDLCState):
    #     """
    #         Reviews the product requirements and returns the decision in state
    #     """
    #     print("----- Product Owner Review ----")
    #     requirements = state['requirements']
    #     user_stories = state['user_stories']

    #     # collect any issues
    #     decision = "approved"
    #     issues = []

    #     if len(requirements) < 3:
    #         decision = "feedback"
    #         issues.append("In suffcient number of requirements. Need atleast 3 core requirements")

    #     # check for the title and description lengths
    #     for story in user_stories:
    #         story_id = getattr(story, 'id', 'unknown')
    #         story_title = getattr(story, 'title', '')
    #         story_description = getattr(story, 'description', '')
    #         if not hasattr(story, 'title') or len(story_title) < 10:
    #             decision = 'feedback'
    #             issues.append(f"User story {story_id} has an insufficient title")

    #         if not hasattr(story, 'description') or len(story_description) < 30:
    #             decision = 'feedback'
    #             issues.append(f"User story {story_id} needs a more detailed description")
        
    #     # Return a dictionary with state updates
    #     return {
    #             "product_decision": decision, 
    #             "feedback_reasons": issues if issues else ["All requirements and user stories meets quality standards"]
    #     }