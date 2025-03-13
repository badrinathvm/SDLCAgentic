
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
        design_feedback = None
        if 'design_documents' in state:
            design_feedback = state.get('design_documents','')['feedback_reason']

        functional_documents = self.generate_functional_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories,
            design_feedback=design_feedback
        )

        technical_documents = self.generate_technical_design(
            project_name=project_name,
            requirements=requirements,
            user_stories=user_stories,
            design_feedback=design_feedback
        )

        design_documents = DesignDocument(
            functional=functional_documents,
            technical = technical_documents
        )

        return {
            **state,
            "current_node": "create_design_document",
            "next_required_input": "design_review",
            "design_documents": design_documents,
            "technical_documents": technical_documents
        }
    
    def generate_functional_design(self, project_name, requirements, user_stories, design_feedback):
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

             {f"When creating this functional design document, please incorporate the following feedback about the requirements: {design_feedback}" if design_feedback else ""}
            
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
    
    def generate_technical_design(self, project_name, requirements, user_stories, design_feedback):
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

                {f"When creating this technical design document, please incorporate the following feedback about the requirements: {design_feedback}" if design_feedback else ""}
                
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
    
    def design_review_router(self, state: SDLCState):
        """
            Evaluates design review is required or not.
        """
        return state['design_documents']['review_status']

    def design_review(self, state: SDLCState):
        """
            Performs the Design review
        """
        pass

    def generate_code(self, state: SDLCState):
        """
            Generates the code for the requirements in the design document
        """
        print("----- Generating the code ----")
        prompt = f"""
        Generate Python code based on the following SDLC state:

            Project Name: {state['project_name']}

            ### Requirements:
            {"".join([f"- {req}\n" for req in state['requirements']])}

            ### User Stories:
            {"".join([f"- {story['title']}: {story['description']}\n" for story in state['user_stories']])}

            ### Functional Design Document:
            {state['design_documents']['functional']}

            ### Technical Design Document:
            {state['design_documents']['technical']}

            The generated Python code should include:

            1. **Comments for Requirements**: Add each requirement as a comment in the generated code.
            2. **User Stories Implementation**: Include placeholders for each user story, with its description and acceptance criteria as comments.
            3. **Functional Design Reference**: Incorporate the functional design document content as a comment in the relevant section.
            4. **Technical Design Reference**: Include the technical design document details in a comment under its section.
            5. **Modularity**: Structure the code to include placeholders for different functionalities derived from the SDLC state, with clear comments indicating where each functionality should be implemented.
            6. **Python Formatting**: The generated code should follow Python syntax and best practices.

            Ensure the output code is modular, well-commented, and ready for development.
        """
        response = self.llm.invoke(prompt)
        next_required_input = "coming_soon" if state['design_documents']['review_status'] == "approved" else "create_design_document"
        return {'code_generated': response.content, 'next_required_input': next_required_input, 'current_node': 'generate_code' }
