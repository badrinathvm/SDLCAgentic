
from src.llm.openai_llm import OpenAILLM
from src.state.sdlc_state import DesignDocument, SDLCState
from langchain.agents import Tool
from datetime import datetime
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
        next_required_input = "code_review" if state['design_documents']['review_status'] == "approved" else "create_design_document"
        code_review_comments = self.get_code_review_comments(code=response.content)
        return {
                'code_generated': response.content, 
                'next_required_input': next_required_input, 
                'current_node': 'generate_code',
                'code_review_comments': code_review_comments
            }
    
    def get_code_review_comments(self, code: str):
        """
        Generate code review comments for the provided code
        """
        print("----- Generating code review comments ----")
        
        # Create a prompt for the LLM to review the code
        prompt = f"""
            You are a coding expert. Please review the following code and provide detailed feedback:
            ```
            {code}
            ```
            Focus on:
            1. Code quality and best practices
            2. Potential bugs or edge cases
            3. Performance considerations
            4. Security concerns
            
            End your review with an explicit APPROVED or NEEDS_FEEDBACK status.
        """
        
        # Get the review from the LLM
        response = self.llm.invoke(prompt)
        review_comments = response.content
        return review_comments
        

    def code_review(self, state: SDLCState):
        """
            Performs the Design review
        """
        pass

    def code_review_router(self, state: SDLCState):
        """
            Evaluates design review is required or not.
        """
        return state['code_review_status']
    
    def security_recommendations(self, state: SDLCState):
        """
            Performs security review of the code generated
        """
         # Get the generated code from the state
        code_generated = state.get('code_generated', '')

         # Create a prompt for the LLM to review the code for security concerns
        prompt = f"""
            You are a security expert. Please review the following Python code for potential security vulnerabilities:
            ```
            {code_generated}
            ```
            Focus on:
            1. Identifying potential security risks (e.g., SQL injection, XSS, insecure data handling).
            2. Providing recommendations to mitigate these risks.
            3. Highlighting any best practices that are missing.

            End your review with an explicit APPROVED or NEEDS_FEEDBACK status.
        """

         # Invoke the LLM to perform the security review
        response = self.llm.invoke(prompt)
        security_review_comments = response.content

        return {
            **state,
            "current_node": "code_review",
            "next_required_input": "security_review",
            "security_review_comments": security_review_comments
        }
    
    def security_review(self, state: SDLCState):
        """
            Performs the security review
        """
        pass

    def security_review_router(self, state: SDLCState):
        """
            Evaluates design review is required or not.
        """
        return state['security_review_status']
    
    def generate_test_cases(self, state: SDLCState):
        """
            Generates the test cases based on the generated code and code review comments
        """
        print("----- Generating Test Cases ----")
    
        # Get the generated code and code review comments from the state
        code_generated = state.get('code_generated', '')
        code_review_comments = state.get('code_review_comments', '')

         # Create a prompt for the LLM to generate test cases
        prompt = f"""
            You are a software testing expert. Based on the following Python code and its review comments, generate comprehensive test cases:
            
            ### Code:
            ```
                {code_generated}
                ```

                ### Code Review Comments:
                {code_review_comments}

                Focus on:
                1. Covering all edge cases and boundary conditions.
                2. Ensuring functional correctness of the code.
                3. Including both positive and negative test cases.
                4. Writing test cases in Python's `unittest` framework format.

                Provide the test cases in Python code format, ready to be executed.
        """

         # Invoke the LLM to generate the test cases
        response = self.llm.invoke(prompt)
        test_cases = response.content

        # Update the state with the generated test cases
        return {
            **state,
            "current_node": "generate_test_cases",
            "next_required_input": "test_cases_review",
            "test_cases": test_cases,
        }
    
    def test_cases_review(self, state: SDLCState):
        """
            Process the human decision from the UI
        """
        print("----- Test cases Review -----")
        # Mark that human input is required.
        # return {
        #     "human_input_required": True,
        #     "timestamp": datetime.now().isoformat()
        # }
        pass
    
    def test_cases_review_router(self, state: SDLCState):
        """
            Evaluates tests cases review is required or not.
        """
        return state['test_case_review_status']
    
    def qa_testing(self, state: SDLCState):
        """
            Performs QA testing based on the generated code and test cases
        """
        print("----- Performing QA Testing ----")
        # Get the generated code and test cases from the state
        code_generated = state.get('code_generated', '')
        test_cases = state.get('test_cases', '')

        # Create a prompt for the LLM to simulate running the test cases
        prompt = f"""
            You are a QA testing expert. Based on the following Python code and test cases, simulate running the test cases and provide feedback:
            
            ### Code:
            ```
            {code_generated}
            ```

            ### Test Cases:
            ```
            {test_cases}
            ```

            Focus on:
            1. Identifying which test cases pass and which fail.
            2. Providing detailed feedback for any failed test cases, including the reason for failure.
            3. Suggesting improvements to the code or test cases if necessary.

            Provide the results in the following format:
            - Test Case ID: [ID]
            Status: [Pass/Fail]
            Feedback: [Detailed feedback if failed]
        """

        # Invoke the LLM to simulate QA testing
        response = self.llm.invoke(prompt)
        qa_testing_comments = response.content

        # Update the state with the QA testing results
        return {
            **state,
            "current_node": "qa_testing",
            "next_required_input": "qa_testing_review" if state['test_case_review_status'] == "approved" else "generate_test_cases",
            "qa_testing_status": state['test_case_review_status'],
            "qa_testing_comments": qa_testing_comments
        }
    
    def deployment(self, state: SDLCState):
        """
            Performs teh deployment
        """
        print("----- Performing Deployment ----")

        # Get the generated code and QA testing status from the state
        code_generated = state.get('code_generated', '')
        qa_testing_status = state.get('qa_testing_status', '')

        # Create a prompt for the LLM to simulate deployment
        prompt = f"""
            You are a DevOps expert. Based on the following Python code, simulate the deployment process and provide feedback:
            
            ### Code:
            ```
            {code_generated}
            ```

            Focus on:
            1. Identifying potential deployment issues (e.g., missing dependencies, configuration errors).
            2. Providing recommendations to resolve any issues.
            3. Confirming whether the deployment is successful or needs further action.

            Provide the results in the following format:
            - Deployment Status: [Success/Failed]
            - Feedback: [Detailed feedback on the deployment process]
        """

        # Invoke the LLM to simulate deployment
        response = self.llm.invoke(prompt)
        deployment_feedback = response.content

         # Determine the deployment status based on the feedback
        if "SUCCESS" in deployment_feedback.upper():
            deployment_status = "success"
        else:
            deployment_status = "failed"

        # Update the state with the deployment results
        return {
            **state,
            "current_node": "deployment",
            "next_required_input": "end" if deployment_status == "success" else "qa_testing",
            "deployment_status": deployment_status,
            "deployment_feedback": deployment_feedback
        }
    
    def qa_testing_review(self, state: SDLCState):
        """
            Process the human decision from the UI
        """
        print("----- Test cases Review -----")
        # Mark that human input is required.
        # return {
        #     "human_input_required": True,
        #     "timestamp": datetime.now().isoformat()
        # }
        pass

    def qa_testing_review_router(self, state: SDLCState):
        """
            Evaluates tests cases review is required or not.
        """
        return state['qa_testing_status']
