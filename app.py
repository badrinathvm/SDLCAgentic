import uvicorn
from fastapi import FastAPI, Request

from src.graph.graph_builder import GraphBuilder
from src.llm.groq_llm import GroqLLM

app = FastAPI()

@app.post("/sdlc/workflow/start")
async def initiliaze_graph(request: Request):
    """
        Initializes a graph
    """
    data = await request.json()
    project_name = data.get('project_name', '')
    requirements = data.get('requirements', '')

    # Get the llm instance
    llm = GroqLLM().get_llm()

    # Create an instance of graph builder
    graph_builder = GraphBuilder(llm=llm)
    graph = graph_builder.setup_graph()

    state = await graph.ainvoke({'project_name': project_name, 'requirements': requirements})
    if graph:
        return {"data" : state}
    else:
        return {"data": "fail"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

