from unittest.mock import MagicMock, Mock

import pytest
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from fabric_agent_action.agents import AgentBuilder, ReActAgent, RouterAgent
from fabric_agent_action.fabric_tools import FabricTools


@pytest.fixture
def llm_provider():
    mock_llm_provider = Mock()
    mock_llm = Mock()
    mock_llm.use_system_message = True
    mock_llm.llm = MagicMock()
    mock_llm_provider.createAgentLLM.return_value = mock_llm
    return mock_llm_provider


@pytest.fixture
def mock_fabric_tools():
    def test_tool(input: str):
        """test tool

        Args:
            input (str): input
        """
        return input

    tools = Mock(spec=FabricTools)
    tools.get_fabric_tools.return_value = [test_tool]
    return tools


# Tests for AgentBuilder
def test_agent_builder_with_valid_agent_type(llm_provider, mock_fabric_tools):
    builder = AgentBuilder("router", llm_provider, mock_fabric_tools)
    graph = builder.build()
    assert graph is not None


def test_agent_builder_with_invalid_agent_type(llm_provider, mock_fabric_tools):
    builder = AgentBuilder("invalid_type", llm_provider, mock_fabric_tools)
    with pytest.raises(ValueError) as exc_info:
        builder.build()
    assert str(exc_info.value) == "Unknown agent type: invalid_type"


# Tests for RouterAgent
def test_router_agent_build_graph(llm_provider, mock_fabric_tools):
    agent = RouterAgent(llm_provider, mock_fabric_tools)
    graph = agent.build_graph()
    assert graph is not None


# Tests for ReActAgent
def test_react_agent_build_graph(llm_provider, mock_fabric_tools):
    agent = ReActAgent(llm_provider, mock_fabric_tools)
    graph = agent.build_graph()
    assert graph is not None


def test_react_agent_tools_condition(llm_provider, mock_fabric_tools):
    agent = ReActAgent(llm_provider, mock_fabric_tools)

    # Test state with no tool calls
    state = {"messages": [HumanMessage(content="test")], "max_num_turns": 10}
    result = agent._tools_condition(state)
    assert result == "__end__"

    # Test state with tool calls
    mock_message = MagicMock()
    mock_message.tool_calls = [Mock()]
    state = {"messages": [mock_message], "max_num_turns": 10}
    result = agent._tools_condition(state)
    assert result == "tools"


def test_react_agent_max_turns_exceeded(llm_provider, mock_fabric_tools):
    agent = ReActAgent(llm_provider, mock_fabric_tools)

    # Create state with maximum number of turns exceeded
    tool_messages = [ToolMessage(content="test", tool_call_id="1", name="test") for _ in range(11)]
    state = {"messages": tool_messages, "max_num_turns": 10}

    result = agent._tools_condition(state)
    assert result == "__end__"


# Test assistant method in ReActAgent
def test_react_agent_assistant(llm_provider, mock_fabric_tools):
    agent = ReActAgent(llm_provider, mock_fabric_tools)
    mock_llm_with_tools = Mock()
    mock_llm_with_tools.invoke.return_value = "test response"
    mock_agent_msg = SystemMessage(content="test")

    state = {"messages": [HumanMessage(content="test")]}
    result = agent._assistant(mock_llm_with_tools, mock_agent_msg, state)

    assert "messages" in result
    mock_llm_with_tools.invoke.assert_called_once()
