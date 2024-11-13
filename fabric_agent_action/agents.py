import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, llm_provider: LLMProvider, fabric_tools: FabricTools):
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build_graph(self) -> StateGraph:
        """Build and return the agent's graph"""
        raise NotImplementedError


class AgentBuilder:
    def __init__(self, agent_type: str, llm_provider: LLMProvider, fabric_tools):
        self.agent_type = agent_type
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

        self._agents = {"single_command": SingleCommandAgent, "react": ReActAgent}

    def build(self) -> StateGraph:
        """Build and return appropriate agent type"""
        agent_class = self._agents.get(self.agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        return agent_class(self.llm_provider, self.fabric_tools).build_graph()


class SingleCommandAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider, fabric_tools):
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build_graph(self):
        logger.debug(f"[{SingleCommandAgent.__name__}] building graph...")

        llm = self.llm_provider.createAgentLLM()
        llm_with_tools = llm.llm.bind_tools(self.fabric_tools.get_fabric_tools())

        msg_content = """You are a fabric assistant, that is tasked to run actions using fabric tools on given input.

        I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
        """

        if llm.use_system_message:
            agent_msg = SystemMessage(content=msg_content)
        else:
            agent_msg = HumanMessage(content=msg_content)

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


class ReActAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider, fabric_tools):
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build_graph(self):
        logger.debug(f"[{ReActAgent.__name__}] building graph...")

        llm = self.llm_provider.createAgentLLM()
        llm_with_tools = llm.llm.bind_tools(self.fabric_tools.get_fabric_tools())

        msg_content = """You are a fabric assistant, that is tasked to run actions using fabric tools on given input.

        I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
        """

        if llm.use_system_message:
            agent_msg = SystemMessage(content=msg_content)
        else:
            agent_msg = HumanMessage(content=msg_content)

        def assistant(state):
            return {
                "messages": [llm_with_tools.invoke([agent_msg] + state["messages"])]
            }

        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(self.fabric_tools.get_fabric_tools()))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        graph = builder.compile()

        return graph
