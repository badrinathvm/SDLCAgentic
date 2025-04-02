# SoftwareAgentic

This project was generated using a LangGraph project structure generator.

## Modular Project Structure

- `src/`: Source code
  - `graph/`: LangGraph graph definitions
  - `nodes/`: Custom LangGraph nodes
  - `state/`: Graph state
  - `tools/`: Custom Tools
  -  `llm/` : LLM configurations to be used for the project
  -  `cache/`: Cache implementation files for staoring the state
`.env`: Environment variables configuration

## Graph: 

<img width="326" alt="SDLC_Graph_Flow" src="https://github.com/user-attachments/assets/15a57181-3a78-4ecc-ae22-bdea707f7229" />

## Workflow Overview

### ✅ Workflow Initialization
Automated project creation to jumpstart the development process
```
POST: /sdlc/workflow/start - Initializes the project which creates the `task_id`

Response: 
    {
        "task_id": "sdlc-task-54957c4c",
        "status": "in_progress",
        "next_required_input": "requirements",
        "progress": 10,
        "current_node": "project_initilization"
    }
```

### ✅ Interactive User Input Management
Seamless handling of critical review stages:
- Requirements collection
- Product owner signoff
- Code review integration
- Security assessment
- Test case validation
- QA testing feedback

## API Endpoints

### Requirements Collection
```
POST : sdlc/workflow/{{task_id}}/requirements

Request Body: 
{
    "task": "Users should be able to browse movies, select seats, and make payments seamlessly through the platform."
}
```

### product_owner_review / design_review / code_review / security_review / test_cases_review / qa_testing_review

```
POST : sdlc/workflow/{{task_id}}/product_owner_review

Request Body: 
{
    "review_status": "approved",
    "feedback_reason": ""
}

Response: 
{
  "task_id": "sdlc-task-1234",
  "data": {
    "project_name": "Movie Platform",
    "requirements": [
      "Allow users to browse movies.",
      "Enable users to select seats.",
      "Provide payment functionality."
    ],
    "user_stories": [
      {
        "id": 1,
        "title": "Browse Movies",
        "description": "As a user, I want to browse available movies.",
        "status": "To Do"
      },
      {
        "id": 2,
        "title": "Select Seats",
        "description": "As a user, I want to select seats for my booking.",
        "status": "To Do"
      },
      {
        "id": 3,
        "title": "Make Payment",
        "description": "As a user, I want to pay for my tickets.",
        "status": "To Do"
      }
    ],
    "progress": 10,
    "next_required_input": "design_review",
    "current_node": "create_design_document",
    "status": "in_progress",
    "product_decision": "approved",
    "feedback_reason": "",
    "design_documents": {
      "functional": "# Functional Design Document\n## 1. Introduction\nThis document outlines the functional design of the Movie Platform.\n\n## 2. User Roles\n- Guest User\n- Registered User\n- Admin\n\n## 3. Features\n- Browse movies\n- Select seats\n- Make payments",
      "technical": "# Technical Design Document\n## 1. Architecture\nMicroservices architecture with RESTful APIs.\n\n## 2. Technology Stack\n- Backend: Java\n- Frontend: React\n- Database: PostgreSQL\n\n## 3. API Endpoints\n- GET /movies\n- POST /bookings\n- POST /payments",
      "review_status": "",
      "feedback_reason": ""
    }
  }
}

```


## Demo Video : 

https://github.com/user-attachments/assets/8459f04b-7590-46cc-9bef-71ed49a45acc
