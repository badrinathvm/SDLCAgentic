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
    
    requirements = data.get('requirements', '')

     # Get the graph instance from the app state
    graph = app.state.graph

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

    delete_from_redis(task_id)

    return {"task_id": task_id, "data": state}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

