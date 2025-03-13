
from src.llm.openai_llm import OpenAILLM
from src.state.sdlc_state import DesignDocument, SDLCState
from langchain.agents import Tool
import re
import os

from src.tools.markdown_tool import clean_markdown

class DesignNode:
    def __init__(self, llm):
        self.llm = llm    
            
    def create_design_document(self, state: SDLCState):
        """
        Generates the Design document functional and technical
        """
        print("----- Creating Design Document ----")
        requirements = state.get('requirements', '')
        user_stories = state.get('user_stories', '')
        project_name = state.get('project_name', '')

        functional_documents = self.generate_functional_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories
        )

        design_documents = DesignDocument(
            functional=functional_documents
        )

        return {
            **state,
            "design_documents": design_documents
        }
    
    def generate_functional_design(self, project_name, requirements, user_stories):
        """
        Helper method to generate functional design document
        """
        prompt = f"""
            Create a comprehensive functional design document for {project_name} in Markdown format. The document should adhere to proper Markdown syntax, including appropriate headers (using # for main titles, ## for sections, etc.), bullet points, tables, and code blocks where applicable.

            The document should include the following sections with proper formatting:
                1.	Introduction and Purpose
            Provide a brief introduction and the purpose of the system or project.
                2.	Project Scope
            Define the scope of the project, including its boundaries, goals, and features.
                3.	User Roles and Permissions
            List and describe the roles of users in the system and the corresponding permissions each role has.
                4.	Functional Requirements Breakdown
            Break down the functional requirements of the system with proper bullet points or sub-sections.
                5.	User Interface Design Guidelines
            Describe the UI design principles, including layout, accessibility, and responsive design.
                6.	Business Process Flows
            Provide any necessary business process flow diagrams or descriptions. Use Mermaid syntax for flowcharts if applicable.
                7.	Data Entities and Relationships
            List the entities (such as Users, Products, Orders, etc.) and their relationships in the system, including a table for clarity.
                8.	Validation Rules
            Specify the validation rules for key data inputs or processes in the system.
                9.	Reporting Requirements
            Define any reporting needs (e.g., sales reports, user analytics, etc.), using bullet points to list them.
                10.	Integration Points
            Detail the external systems or APIs that the project will integrate with, along with their purpose and any requirements.

            The document should also include the following sections:
                •	Requirements:
                •	Format the requirements as a list of bullet points: {self._format_list(requirements)}.
                •	User Stories:
                •	Format the user stories as a list of bullet points: {self._format_user_stories(user_stories)}.

            Ensure that the document maintains proper Markdown formatting throughout, with consistent use of headings, subheadings, bullet points, tables, and code blocks. Additionally, ensure that any technical details are presented in a clear, structured manner, using the appropriate Markdown syntax.
        """
        # invoke the llm
        response = self.llm.invoke(prompt)

        # content = self.fix_markdown(content=response.content)
        return response.content    

    def _format_list(self, items):
        """Format list items nicely for prompt"""
        return '\n'.join([f"- {item}" for item in items])
    
    def _format_user_stories(self, stories):
        """Format user stories nicely for prompt"""
        formatted_stories = []
        for story in stories:
            if hasattr(story, 'id') and hasattr(story, 'title') and hasattr(story, 'description'):
                # Handle class instance
                formatted_stories.append(f"- ID: {story.id}\n  Title: {story.title}\n  Description: {story.description}")
            elif isinstance(story, dict):
                # Handle dictionary
                formatted_stories.append(f"- ID: {story.get('id', 'N/A')}\n  Title: {story.get('title', 'N/A')}\n  Description: {story.get('description', 'N/A')}")
        return '\n'.join(formatted_stories)
