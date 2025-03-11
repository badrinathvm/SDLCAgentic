from langgraph.graph import StateGraph, START, END
from src.nodes.sdlc_node import SDLCNode
from src.state.sdlc_state import SDLCState
from langgraph.checkpoint.memory import MemorySaver

class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        self.builder = StateGraph(SDLCState)
        self.memory = MemorySaver()

    def build_graph(self):
        """
            Configure the graph by adding nodes, edges
        """
        self.sdlc_node = SDLCNode(llm=self.llm)

        # Nodes
        self.builder.add_node("project_initilization", self.sdlc_node.project_initilization)
        self.builder.add_node("get_requirements", self.sdlc_node.get_requirements)
        self.builder.add_node("auto_generate_user_stories", self.sdlc_node.auto_generate_user_stories)

        # Edges
        self.builder.add_edge(START, "project_initilization")
        self.builder.add_edge("project_initilization", "get_requirements")
        self.builder.add_edge("get_requirements", "auto_generate_user_stories")
        self.builder.add_edge("auto_generate_user_stories", END)
       
        # self.builder.add_edge("auto_generate_user_stories", END)
        return self.builder

    def setup_graph(self):
        self.graph = self.build_graph()
        return self.graph.compile(interrupt_before=['get_requirements'], checkpointer=self.memory)