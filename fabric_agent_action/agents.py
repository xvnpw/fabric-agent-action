import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


class AgentBuilder:
    def __init__(self, agent_type: str, llm_provider: LLMProvider, fabric_tools):
        self.agent_type = agent_type
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build(self):
        if self.agent_type == "single_command":
            return SingleCommandAgent(
                self.llm_provider, self.fabric_tools
            ).build_graph()
        elif self.agent_type == "react":
            return ReActAgent().build_graph()


class SingleCommandAgent:
    def __init__(self, llm_provider: LLMProvider, fabric_tools):
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build_graph(self):
        logger.debug("[single-command-agent] building graph...")

        llm, use_system_message = self.llm_provider.createAgentLLM()
        llm_with_tools = llm.bind_tools(self.fabric_tools.get_fabric_tools())

        if use_system_message:
            agent_msg = SystemMessage(
                content="""You are a fabric assistant, that is tasked to run actions using fabric tools on given input. 
                
                I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
                """
            )
        else:
            agent_msg = HumanMessage(
                content="""You are a fabric assistant, that is tasked to run actions using fabric tools on given input. 
                
                I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
                """
            )

        def assistant(state):
            return {
                "messages": [llm_with_tools.invoke([agent_msg] + state["messages"])]
            }

        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(self.fabric_tools.get_fabric_tools()))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", END)
        graph = builder.compile()

        return graph


class ReActAgent:
    def build_graph(self):
        raise NotImplementedError()
