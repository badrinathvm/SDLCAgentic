
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

        technical_documents = self.generate_technical_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories
        )

        design_documents = DesignDocument(
            functional=functional_documents,
            technical = technical_documents
        )

        return {
            **state,
            "design_documents": design_documents,
            "technical_documents": technical_documents
        }
    
    def generate_functional_design(self, project_name, requirements, user_stories):
        """
        Helper method to generate functional design document
        """
        print("----- Creating Functional Design Document ----")
        prompt = f"""
            Create a comprehensive functional design document for {project_name} in Markdown format.
    
            The document should use proper Markdown syntax with headers (# for main titles, ## for sections, etc.), 
            bullet points, tables, and code blocks where appropriate.
            
            Requirements:
            {self._format_list(requirements)}
            
            User Stories:
            {self._format_user_stories(user_stories)}
            
            The functional design document should include the following sections, each with proper Markdown formatting:
            
            # Functional Design Document: {project_name}
            
            ## 1. Introduction and Purpose
            ## 2. Project Scope
            ## 3. User Roles and Permissions
            ## 4. Functional Requirements Breakdown
            ## 5. User Interface Design Guidelines
            ## 6. Business Process Flows
            ## 7. Data Entities and Relationships
            ## 8. Validation Rules
            ## 9. Reporting Requirements
            ## 10. Integration Points
            
            Make sure to maintain proper Markdown formatting throughout the document.
        """
        # invoke the llm
        response = self.llm.invoke(prompt)

        # content = self.fix_markdown(content=response.content)
        return response.content    
    
    def generate_technical_design(self, project_name, requirements, user_stories):
            """
                Helper method to generate technical design document in Markdown format
            """
            print("----- Creating Technical Design Document ----")
            prompt = f"""
                Create a comprehensive technical design document for {project_name} in Markdown format.
                
                The document should use proper Markdown syntax with headers (# for main titles, ## for sections, etc.), 
                bullet points, tables, code blocks, and diagrams described in text form where appropriate.
                
                Requirements:
                {self._format_list(requirements)}
                
                User Stories:
                {self._format_user_stories(user_stories)}
                
                The technical design document should include the following sections, each with proper Markdown formatting:
                
                # Technical Design Document: {project_name}

                 ## 1. System Architecture
                ## 2. Technology Stack and Justification
                ## 3. Database Schema
                ## 4. API Specifications
                ## 5. Security Considerations
                ## 6. Performance Considerations
                ## 7. Scalability Approach
                ## 8. Deployment Strategy
                ## 9. Third-party Integrations
                ## 10. Development, Testing, and Deployment Environments
                
                For any code examples, use ```language-name to specify the programming language.
                For database schemas, represent tables and relationships using Markdown tables.
                Make sure to maintain proper Markdown formatting throughout the document.
            """
            response = self.llm.invoke(prompt)
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
