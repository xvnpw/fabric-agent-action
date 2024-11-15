import pytest
from unittest.mock import Mock
import io
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from fabric_agent_action.config import AppConfig
from fabric_agent_action.graphs import (
    BaseGraphExecutor,
    SingleCommandGraphExecutor,
    ReActGraphExecutor,
    GraphExecutorFactory,
)


@pytest.fixture
def mock_config():
    config = Mock(spec=AppConfig)
    config.output_file = io.StringIO()
    config.agent_preamble = "AI Assistant:"
    config.agent_preamble_enabled = True
    config.fabric_max_num_turns = 5
    config.agent_type = "single_command"
    return config


@pytest.fixture
def mock_graph():
    return Mock(spec=CompiledStateGraph)


@pytest.fixture
def mock_messages_state():
    return {"messages": [HumanMessage(content="Hello"), AIMessage(content="Hi there!")]}


class TestBaseGraphExecutor:
    class ConcreteExecutor(BaseGraphExecutor):
        def execute(self, graph: CompiledStateGraph, input_str: str) -> None:
            pass

        def _invoke_graph(self, graph: CompiledStateGraph, input_str: str) -> Any:
            pass

        def _write_output(self, messages_state: Any) -> None:
            pass

    def test_format_output_with_preamble(self, mock_config):
        executor = self.ConcreteExecutor(mock_config)
        content = "Test message"
        expected = f"{mock_config.agent_preamble}\n\n{content}"
        assert executor._format_output(content) == expected

    def test_format_output_without_preamble(self, mock_config):
        mock_config.agent_preamble_enabled = False
        executor = self.ConcreteExecutor(mock_config)
        content = "Test message"
        assert executor._format_output(content) == content


class TestSingleCommandGraphExecutor:
    def test_invoke_graph(self, mock_config, mock_graph):
        executor = SingleCommandGraphExecutor(mock_config)
        input_str = "Hello"
        executor._invoke_graph(mock_graph, input_str)
        mock_graph.invoke.assert_called_once()

    def test_write_output(self, mock_config, mock_messages_state):
        executor = SingleCommandGraphExecutor(mock_config)
        executor._write_output(mock_messages_state)
        assert mock_config.output_file.getvalue() == f"{mock_config.agent_preamble}\n\nHi there!"


class TestReActGraphExecutor:
    def test_invoke_graph(self, mock_config, mock_graph):
        mock_config.agent_type = "react"
        executor = ReActGraphExecutor(mock_config)
        input_str = "Hello"
        executor._invoke_graph(mock_graph, input_str)
        mock_graph.invoke.assert_called_once()

    def test_write_output_valid_message(self, mock_config, mock_messages_state):
        executor = ReActGraphExecutor(mock_config)
        executor._write_output(mock_messages_state)
        assert mock_config.output_file.getvalue() == f"{mock_config.agent_preamble}\n\nHi there!"

    def test_write_output_invalid_message(self, mock_config):
        executor = ReActGraphExecutor(mock_config)
        invalid_state = {"messages": [HumanMessage(content="Hello")]}
        with pytest.raises(ValueError, match="Invalid or empty AI message"):
            executor._write_output(invalid_state)

    def test_max_num_turns_passed_to_graph(self, mock_config, mock_graph):
        mock_config.agent_type = "react"
        mock_config.fabric_max_num_turns = 10
        executor = ReActGraphExecutor(mock_config)

        executor._invoke_graph(mock_graph, "Test input")

        mock_graph.invoke.assert_called_once_with(
            {"messages": [HumanMessage(content="Test input")], "max_num_turns": 10}
        )

    def test_max_num_turns_zero(self, mock_config, mock_graph):
        mock_config.agent_type = "react"
        mock_config.fabric_max_num_turns = 0
        executor = ReActGraphExecutor(mock_config)

        executor._invoke_graph(mock_graph, "Test input")

        mock_graph.invoke.assert_called_once_with(
            {"messages": [HumanMessage(content="Test input")], "max_num_turns": 0}
        )


class TestGraphExecutorFactory:
    def test_create_single_command_executor(self, mock_config):
        executor = GraphExecutorFactory.create(mock_config)
        assert isinstance(executor, SingleCommandGraphExecutor)

    def test_create_react_executor(self, mock_config):
        mock_config.agent_type = "react"
        executor = GraphExecutorFactory.create(mock_config)
        assert isinstance(executor, ReActGraphExecutor)

    def test_create_unknown_executor(self, mock_config):
        mock_config.agent_type = "unknown"
        with pytest.raises(ValueError, match="Unknown agent type: unknown"):
            GraphExecutorFactory.create(mock_config)


class TestGraphExecutorIntegration:
    def test_single_command_execution_flow(self, mock_config, mock_graph):
        executor = SingleCommandGraphExecutor(mock_config)
        mock_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="Test input"),
                AIMessage(content="Test response"),
            ]
        }

        executor.execute(mock_graph, "Test input")
        assert mock_config.output_file.getvalue() == f"{mock_config.agent_preamble}\n\nTest response"

    def test_react_execution_flow(self, mock_config, mock_graph):
        mock_config.agent_type = "react"
        executor = ReActGraphExecutor(mock_config)
        mock_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="Test input"),
                AIMessage(content="Test response"),
            ]
        }

        executor.execute(mock_graph, "Test input")
        assert mock_config.output_file.getvalue() == f"{mock_config.agent_preamble}\n\nTest response"

    def test_react_execution_flow_with_max_turns(self, mock_config, mock_graph):
        mock_config.agent_type = "react"
        mock_config.fabric_max_num_turns = 3
        executor = ReActGraphExecutor(mock_config)

        # Simulate a conversation with multiple turns
        mock_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="Test input"),
                AIMessage(content="Intermediate response"),
                HumanMessage(content="Follow-up"),
                AIMessage(content="Final response"),
            ]
        }

        executor.execute(mock_graph, "Test input")

        # Verify max_num_turns was passed correctly
        mock_graph.invoke.assert_called_once_with(
            {"messages": [HumanMessage(content="Test input")], "max_num_turns": 3}
        )

        # Verify final output
        assert mock_config.output_file.getvalue() == f"{mock_config.agent_preamble}\n\nFinal response"
