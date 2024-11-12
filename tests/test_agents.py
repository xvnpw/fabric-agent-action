# test_agents.py
from unittest.mock import Mock

import pytest

from fabric_agent_action.agents import AgentBuilder, SingleCommandAgent
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLM, LLMProvider


@pytest.fixture
def mock_llm_provider():
    provider = Mock(spec=LLMProvider)
    mock_llm = Mock(spec=LLM)
    mock_llm.use_system_message = True
    mock_llm.llm = Mock()
    mock_llm.number_of_tools = 128
    provider.createAgentLLM.return_value = mock_llm
    return provider


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


class TestAgentBuilder:
    def test_build_single_command_agent(self, mock_llm_provider, mock_fabric_tools):
        builder = AgentBuilder("single_command", mock_llm_provider, mock_fabric_tools)
        graph = builder.build()
        assert graph

    def test_invalid_agent_type(self, mock_llm_provider, mock_fabric_tools):
        builder = AgentBuilder("invalid_type", mock_llm_provider, mock_fabric_tools)
        with pytest.raises(ValueError, match="Unknown agent type: invalid_type"):
            builder.build()


class TestSingleCommandAgent:
    def test_system_message_creation(self, mock_llm_provider, mock_fabric_tools):
        agent = SingleCommandAgent(mock_llm_provider, mock_fabric_tools)

        # Get the LLM mock
        llm_mock = mock_llm_provider.createAgentLLM()
        llm_mock.use_system_message = True

        graph = agent.build_graph()

        # The graph was created, now we can verify the message type
        # This requires inspecting the assistant node's function
        nodes = graph.nodes
        assert "assistant" in nodes

        # Verify that bind_tools was called
        llm_mock.llm.bind_tools.assert_called_once_with(
            mock_fabric_tools.get_fabric_tools()
        )
