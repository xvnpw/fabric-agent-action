import io
import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage, HumanMessage

from fabric_agent_action.graphs import GraphExecutor
from fabric_agent_action.config import AppConfig


@pytest.fixture
def mock_config():
    config = Mock(spec=AppConfig)
    config.output_file = io.StringIO()
    config.fabric_max_num_turns = 3
    config.agent_preamble = "Agent:"
    config.agent_preamble_enabled = True
    return config


@pytest.fixture
def graph_executor(mock_config):
    return GraphExecutor(mock_config)


@pytest.fixture
def mock_graph():
    graph = Mock()
    return graph


def test_execute_success(graph_executor, mock_graph):
    mock_graph.invoke.return_value = {
        "messages": [HumanMessage(content="Hello"), AIMessage(content="Response")]
    }

    graph_executor.execute(mock_graph, "Hello")

    assert graph_executor.config.output_file.getvalue() == "Agent:\n\nResponse"


def test_execute_with_preamble_disabled(mock_config, mock_graph):
    mock_config.agent_preamble_enabled = False
    executor = GraphExecutor(mock_config)

    mock_graph.invoke.return_value = {
        "messages": [HumanMessage(content="Hello"), AIMessage(content="Response")]
    }

    executor.execute(mock_graph, "Hello")
    assert executor.config.output_file.getvalue() == "Response"


def test_execute_with_empty_ai_message(graph_executor, mock_graph):
    mock_graph.invoke.return_value = {
        "messages": [HumanMessage(content="Hello"), AIMessage(content="")]
    }

    with pytest.raises(ValueError, match="Invalid or empty AI message"):
        graph_executor.execute(mock_graph, "Hello")


def test_execute_with_non_ai_message(graph_executor, mock_graph):
    mock_graph.invoke.return_value = {
        "messages": [HumanMessage(content="Hello"), HumanMessage(content="Response")]
    }

    with pytest.raises(ValueError, match="Invalid or empty AI message"):
        graph_executor.execute(mock_graph, "Hello")


def test_execute_graph_failure(graph_executor, mock_graph):
    mock_graph.invoke.side_effect = Exception("Graph execution failed")

    with pytest.raises(Exception, match="Graph execution failed"):
        graph_executor.execute(mock_graph, "Hello")


def test_invoke_graph_parameters(graph_executor, mock_graph):
    input_str = "Hello"
    graph_executor._invoke_graph(mock_graph, input_str)

    mock_graph.invoke.assert_called_once()
    call_args = mock_graph.invoke.call_args[0][0]

    assert isinstance(call_args["messages"][0], HumanMessage)
    assert call_args["messages"][0].content == input_str
    assert call_args["max_num_turns"] == graph_executor.config.fabric_max_num_turns


def test_format_output_with_preamble(graph_executor):
    content = "Test content"
    formatted = graph_executor._format_output(content)
    assert formatted == f"{graph_executor.config.agent_preamble}\n\n{content}"


def test_format_output_without_preamble(mock_config):
    mock_config.agent_preamble_enabled = False
    executor = GraphExecutor(mock_config)
    content = "Test content"
    formatted = executor._format_output(content)
    assert formatted == content
