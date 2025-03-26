from langgraph.graph import StateGraph, START, END
from src.llm.groq_llm import GroqLLM
from src.nodes.design_doc_node import DesignNode
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
        self.design_node = DesignNode(llm=self.llm)

        # Nodes
        self.builder.add_node("project_initilization", self.sdlc_node.project_initilization)
        self.builder.add_node("get_requirements", self.sdlc_node.get_requirements)
        self.builder.add_node("auto_generate_user_stories", self.sdlc_node.auto_generate_user_stories)
        self.builder.add_node("product_owner_review_decision", self.sdlc_node.product_owner_review_decision) # Routing node
        self.builder.add_node("create_design_document", self.design_node.create_design_document)
        self.builder.add_node("design_review",self.design_node.design_review) # Routing Node
        self.builder.add_node("generate_code", self.design_node.generate_code)
        self.builder.add_node("code_review", self.design_node.code_review) # Routing Node
        self.builder.add_node("generate_security_recommendations", self.design_node.security_recommendations)
        self.builder.add_node("security_review", self.design_node.security_review) # Routing Node
        self.builder.add_node("generate_test_cases", self.design_node.generate_test_cases)
        self.builder.add_node("test_cases_review", self.design_node.test_cases_review) # Routing Node
        self.builder.add_node("qa_testing", self.design_node.qa_testing)
        self.builder.add_node("deployment", self.design_node.deployment)
        self.builder.add_node("qa_testing_review", self.design_node.qa_testing_review) # Routing Node

        # Edges
        self.builder.add_edge(START, "project_initilization")
        self.builder.add_edge("project_initilization", "get_requirements")
        self.builder.add_edge("get_requirements", "auto_generate_user_stories")
        self.builder.add_edge("auto_generate_user_stories", "product_owner_review_decision")
        self.builder.add_conditional_edges(
            "product_owner_review_decision",
            self.sdlc_node.product_decision_router,
            {
                "approved": "create_design_document",
                "feedback": "auto_generate_user_stories"
            }
        )
        self.builder.add_edge("create_design_document", "design_review")
        self.builder.add_conditional_edges(
            "design_review", 
            self.design_node.design_review_router,
            {
                "approved": "generate_code",
                "feedback": "create_design_document"
            }
        )

        self.builder.add_edge("generate_code", "code_review")
        self.builder.add_conditional_edges(
            "code_review",
            self.design_node.code_review_router,
            {
                "approved": "generate_security_recommendations",
                "feedback": "generate_code"
            }
        )

        self.builder.add_edge("generate_security_recommendations", "security_review")
        self.builder.add_conditional_edges(
            "security_review",
            self.design_node.security_review_router,
            {
                "approved": "generate_test_cases",
                "feedback": "generate_code"
            }
        )

        self.builder.add_edge("generate_test_cases", "test_cases_review")
        self.builder.add_conditional_edges(
            "test_cases_review",
            self.design_node.test_cases_review_router,
            {
                "approved": "qa_testing",
                "feedback": "generate_test_cases"
            }
        )
        self.builder.add_edge("qa_testing", "qa_testing_review")
        self.builder.add_conditional_edges(
            "qa_testing_review",
            self.design_node.qa_testing_review_router,
            {
                "approved": "deployment",
                "feedback": "generate_code"
            }
        )
        self.builder.add_edge("deployment", END)

        return self.builder

    def setup_graph(self):
        self.graph = self.build_graph()
        return self.graph.compile(
            interrupt_before=[
                'get_requirements', 
                'product_owner_review_decision', 
                'design_review',
                'code_review',
                'security_review',
                'test_cases_review',
                'qa_testing_review'
            ], checkpointer=self.memory
        )
    

# get the graph 
# llm = GroqLLM().get_llm()
# graph_builder = GraphBuilder(llm)
# graph = graph_builder.build_graph().compile(
#     interrupt_before=[
#         'get_requirements', 
#         'product_owner_review_decision', 
#         'code_review',
#         'security_review',
#         'test_cases_review'
#         ], checkpointer=MemorySaver()
#     )