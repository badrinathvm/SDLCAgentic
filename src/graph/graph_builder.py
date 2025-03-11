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
        self.builder.add_node("auto_generate_user_stories", self.sdlc_node.auto_generate_user_stories)

        # Edges
        self.builder.add_edge(START, "auto_generate_user_stories")
        self.builder.add_edge("auto_generate_user_stories", END)

        return self.builder

    def setup_graph(self):
        self.graph = self.build_graph()
        return self.graph.compile()