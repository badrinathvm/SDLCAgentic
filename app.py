import json
import uvicorn
import uuid
import redis
from fastapi import FastAPI, Request
from src.cache.redis_cache import delete_from_redis, flush_redis_cache, get_state_from_redis, save_state_to_redis
from src.graph.graph_builder import GraphBuilder
from src.llm.groq_llm import GroqLLM
from src.state.sdlc_state import StartWorkflowRequest, StartWorkflowResponse

app = FastAPI()

# Initialize the LLM and GraphBuilder instances once and store them in the app state
@app.on_event("startup")
async def startup_event():
    llm = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm=llm)
    graph = graph_builder.setup_graph()
    app.state.llm = llm
    app.state.graph = graph

@app.post("/sdlc/workflow/start", response_model=StartWorkflowResponse)
async def start_workflow(request: StartWorkflowRequest):
    """
        starts the workflow of the SDLC 
    """
    flush_redis_cache()
    
    # Generate a unique task id
    task_id = f"sdlc-task-{uuid.uuid4().hex[:8]}"

    # Get the graph instance from the app state
    graph = app.state.graph

    # result = graph.invoke({'project_name': request.project_name})
    thread = {"configurable": {"thread_id": task_id}}
    for event in graph.stream({'project_name': request.project_name}, thread, stream_mode="values"):
        print(event)

    current_state = graph.get_state(thread)

    save_state_to_redis(task_id, current_state)

    state = current_state[0]
    response = StartWorkflowResponse(
        task_id=task_id,
        status=state['status'],
        next_required_input=state['next_required_input'],
        progress=state['progress'],
        current_node=state['current_node']
    )
    return response
    

@app.post("/sdlc/workflow/{task_id}/requirements")
async def get_project_requirements(task_id: str, request: Request):
    """
        Gets the project requirements
    """
    data = await request.json()
    task = data.get('task', '')

     # Get the graph instance from the app state
    graph = app.state.graph

     # TODO:: we can do in much better way.
    requirements = split_task_to_requirements(task_statement=task)
    #requirements = data.get('requirements', '')

    saved_state = get_state_from_redis(task_id)
    if saved_state:
        saved_state['requirements'] = requirements

    # update the graph with thread
    thread = {"configurable": {"thread_id": task_id}} 
    graph.update_state(thread, saved_state, as_node="get_requirements")

     # Resume the graph
    state = None
    async for event in graph.astream(None, thread, stream_mode="values"):
        print(f"Event Received: {event}")
        state = event

    # saving the state before asking the product owner for review
    current_state = graph.get_state(thread)
    save_state_to_redis(task_id, current_state)

    return {"task_id": task_id, "data": state}


@app.post("/sdlc/workflow/{task_id}/product_owner_review")
async def product_owner_review(task_id: str, request: Request):
    """
        Review from the product owner
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='product_owner'
    )

@app.post("/sdlc/workflow/{task_id}/design_review")
async def design_review(task_id: str, request: Request):
    """
    Performs the design review
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='design'
    )

@app.post("/sdlc/workflow/{task_id}/code_review")
async def code_review(task_id: str, request: Request):
    """
        Performs the design review
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='code'
    )

@app.post("/sdlc/workflow/{task_id}/security_review")
async def security_review(task_id: str, request: Request):
    """
        Performs the security review
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='security'
    )

@app.post("/sdlc/workflow/{task_id}/test_cases_review")
async def test_cases_review(task_id: str, request: Request):
    """
        Performs the security review
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='testcase'
    )

@app.post("/sdlc/workflow/{task_id}/qa_testing_review")
async def qa_testing_review(task_id: str, request: Request):
    """
        Performs the qa testing review
    """
    return await generic_workflow_review(
        task_id, 
        request, 
        review_type='qa'
    )

def split_task_to_requirements(task_statement: str) -> list[str]:
        """
        Extracts clear and concise requirements from a given task statement.

        Args:
            task_statement (str): The input task statement.

        Returns:
            list[str]: A list of extracted requirements as strings.
        """
        # Prompt for the LLM
        prompt = f"""
        Task: Extract clear and concise requirements from the following statement. Each requirement should be a standalone actionable point. Do not include bullet points in the output.

        Example Input:
            Write an e-commerce application which should allow users to choose products from a catalog, add payments, and submit the order.

        Example Output:
        Allow users to choose products from a catalog.
        Enable users to add payments.
        Provide functionality for users to submit the order.

        Input Statement:
        {task_statement}

        Output:
            """
        # Format the system message
        system_message = prompt
        try:
            # Invoke the LLM to process the prompt
            response = app.state.llm.invoke(system_message)
            # Split the response into individual requirements
            requirements = [line.strip() for line in response.content.splitlines() if line.strip()]
            return requirements
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

async def generic_workflow_review(
    task_id: str, 
    request: Request, 
    review_type: str
):
    """
    Generic workflow review logic
    """
    data = await request.json()

    # Getting review input based on type
    review_status = data.get('review_status', '')
    feedback_reason = data.get('feedback_reason', '')

    # Get the graph instance from the app state
    graph = app.state.graph

    # Fetch the saved state from the redis cache
    saved_state = get_state_from_redis(task_id)
    if saved_state:
        # Dynamically update state based on review type
        if review_type == 'product_owner':
            saved_state['product_decision'] = review_status
            saved_state['feedback_reason'] = feedback_reason
            node_name = "product_owner_review_decision"
        elif review_type == 'design':
            saved_state['design_documents']['review_status'] = review_status
            saved_state['design_documents']['feedback_reason'] = feedback_reason
            node_name = "design_review"
        elif review_type == 'code':
            saved_state['code_review_status'] = review_status
            saved_state['code_review_feedback'] = feedback_reason
            node_name = "code_review"
        elif review_type == 'security':
            saved_state['security_review_status'] = review_status
            saved_state['security_review_feedback'] = feedback_reason
            node_name = "security_review"
        elif review_type == "testcase":
            saved_state['test_case_review_status'] = review_status
            saved_state['test_case_review_feedback'] = feedback_reason
            node_name = "test_cases_review"
        elif review_type == "qa":
            saved_state['qa_testing_status'] = review_status
            saved_state['qa_testing_feedback'] = feedback_reason
            node_name = "qa_testing_review"
        else:
            raise ValueError(f"Unsupported review type: {review_type}")

        # Update the graph with thread
        thread = {"configurable": {"thread_id": task_id}}
        graph.update_state(thread, saved_state, as_node=node_name)

        # Resume the graph stream
        state = None
        async for event in graph.astream(None, thread, stream_mode="values"):
            print(f"{review_type.capitalize()} Review Event Received: {event}")
            state = event
        
        # Saving the state 
        current_state = graph.get_state(thread)
        save_state_to_redis(task_id, current_state)
    
    return {"task_id": task_id, "data": state} if saved_state else {"task_id": task_id}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

