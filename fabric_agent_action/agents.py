import logging
from typing import Literal, Type, Union, Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents"""

    def __init__(self, llm_provider: LLMProvider, fabric_tools: FabricTools) -> None:
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

    def build_graph(self) -> CompiledStateGraph:
        """Build and return the agent's graph"""
        raise NotImplementedError


class AgentBuilder:
    def __init__(
        self, agent_type: str, llm_provider: LLMProvider, fabric_tools: FabricTools
    ) -> None:
        self.agent_type = agent_type
        self.llm_provider = llm_provider
        self.fabric_tools = fabric_tools

        self._agents: dict[str, Type[BaseAgent]] = {
            "single_command": SingleCommandAgent,
            "react": ReActAgent,
        }

    def build(self) -> CompiledStateGraph:
        """Build and return appropriate agent type"""
        agent_class = self._agents.get(self.agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        return agent_class(self.llm_provider, self.fabric_tools).build_graph()


class SingleCommandAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider, fabric_tools: FabricTools) -> None:
        super().__init__(llm_provider, fabric_tools)

    def build_graph(self) -> CompiledStateGraph:
        logger.debug(f"[{SingleCommandAgent.__name__}] building graph...")

        llm = self.llm_provider.createAgentLLM()
        llm_with_tools = llm.llm.bind_tools(self.fabric_tools.get_fabric_tools())

        msg_content = """You are a fabric assistant, that is tasked to run actions using fabric tools on given input.

        I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
        """

        agent_msg: Union[SystemMessage, HumanMessage] = (
            SystemMessage(content=msg_content)
            if llm.use_system_message
            else HumanMessage(content=msg_content)
        )

        def assistant(state: MessagesState):  # type: ignore[no-untyped-def]
            return {
                "messages": [llm_with_tools.invoke([agent_msg] + state["messages"])]  # type: ignore[operator]
            }

        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(self.fabric_tools.get_fabric_tools()))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", END)
        graph = builder.compile()

        return graph


class ReActAgentState(MessagesState):
    max_num_turns: int


class ReActAgent(BaseAgent):
    def __init__(self, llm_provider: LLMProvider, fabric_tools: FabricTools) -> None:
        super().__init__(llm_provider, fabric_tools)

    def _assistant(  # type: ignore[no-untyped-def]
        self,
        llm_with_tools: Any,
        agent_msg: Union[SystemMessage, HumanMessage],
        state: ReActAgentState,
    ):
        return {"messages": [llm_with_tools.invoke([agent_msg] + state["messages"])]}

    def _tools_condition(self, state: ReActAgentState) -> Literal["tools", "__end__"]:
        messages = state.get("messages", [])

        max_num_turns = state.get("max_num_turns", 10)
        num_responses = len([m for m in messages if isinstance(m, ToolMessage)])
        if num_responses >= max_num_turns:
            logger.warning(
                f"Exceeded maximum number of tools turns: {num_responses} >= {max_num_turns}"
            )
            return "__end__"

        ai_message = messages[-1]
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return "__end__"

    def build_graph(self) -> CompiledStateGraph:
        logger.debug(f"[{ReActAgent.__name__}] building graph...")

        llm = self.llm_provider.createAgentLLM()
        llm_with_tools = llm.llm.bind_tools(self.fabric_tools.get_fabric_tools())

        msg_content = """You are a fabric assistant, that is tasked to run actions using fabric tools on given input.

        I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
        """

        agent_msg: Union[SystemMessage, HumanMessage] = (
            SystemMessage(content=msg_content)
            if llm.use_system_message
            else HumanMessage(content=msg_content)
        )

        def assistant(state: ReActAgentState):  # type: ignore[no-untyped-def]
            return self._assistant(llm_with_tools, agent_msg, state)

        def tools_condition(state: ReActAgentState) -> Literal["tools", "__end__"]:
            return self._tools_condition(state)

        builder = StateGraph(ReActAgentState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(self.fabric_tools.get_fabric_tools()))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        graph = builder.compile()

        return graph
