import io
import logging
from typing import Any, Type, Union

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from fabric_agent_action.config import AppConfig

logger = logging.getLogger(__name__)


class BaseGraphExecutor:
    """Base class for all graph executors"""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def execute(self, graph: CompiledStateGraph, input_str: str) -> None:
        raise NotImplementedError

    def _write_output(self, messages_state: Any) -> None:
        raise NotImplementedError

    def _invoke_graph(
        self, graph: CompiledStateGraph, input_str: str
    ) -> Union[dict[str, Any], Any]:
        raise NotImplementedError

    def _execute(self, graph: CompiledStateGraph, input_str: str) -> None:
        try:
            messages_state = self._invoke_graph(graph, input_str)

            for msg in messages_state["messages"]:
                logger.debug(f"Message: {msg.pretty_repr()}")

            self._write_output(messages_state)
        except Exception as e:
            logger.error(f"Graph execution failed: {str(e)}")
            raise

    def _setup_output_encoding(self) -> None:
        if isinstance(self.config.output_file, io.TextIOWrapper):
            try:
                self.config.output_file.reconfigure(encoding="utf-8")
            except Exception as e:
                logger.warning(
                    f"Could not set UTF-8 encoding: {e}. Falling back to system default."
                )

    def _format_output(self, content: str) -> str:
        return (
            f"{self.config.agent_preamble}\n\n{content}"
            if self.config.agent_preamble_enabled
            else content
        )


class GraphExecutorBuilder:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.agent_type = config.agent_type

        self._executors: dict[str, Type[BaseGraphExecutor]] = {
            "single_command": SingleCommandGraphExecutor,
            "react": ReActGraphExecutor,
        }

    def build(self) -> BaseGraphExecutor:
        executor_class = self._executors.get(self.agent_type)
        if not executor_class:
            raise ValueError(f"Unknown agent type: {self.agent_type}")

        return executor_class(self.config)


class SingleCommandGraphExecutor(BaseGraphExecutor):
    def __init__(self, config: AppConfig):
        self.config = config
        self._setup_output_encoding()

    def execute(self, graph: CompiledStateGraph, input_str: str) -> None:
        self._execute(graph, input_str)

    def _invoke_graph(
        self, graph: CompiledStateGraph, input_str: str
    ) -> Union[dict[str, Any], Any]:
        input_messages = [HumanMessage(content=input_str)]
        return graph.invoke(
            {
                "messages": input_messages,
            }
        )

    def _write_output(self, messages_state: Any) -> None:
        last_message = messages_state["messages"][-1]

        content = self._format_output(last_message.content)
        self.config.output_file.write(content)


class ReActGraphExecutor(BaseGraphExecutor):
    def __init__(self, config: AppConfig):
        self.config = config
        self._setup_output_encoding()

    def execute(self, graph: CompiledStateGraph, input_str: str) -> None:
        self._execute(graph, input_str)

    def _invoke_graph(
        self, graph: CompiledStateGraph, input_str: str
    ) -> Union[dict[str, Any], Any]:
        input_messages = [HumanMessage(content=input_str)]
        return graph.invoke(
            {
                "messages": input_messages,
                "max_num_turns": self.config.fabric_max_num_turns,
            }
        )

    def _write_output(self, messages_state: Any) -> None:
        last_message = messages_state["messages"][-1]
        if not isinstance(last_message, AIMessage) or not last_message.content:
            raise ValueError("Invalid or empty AI message")

        content = self._format_output(
            last_message.content
            if isinstance(last_message.content, str)
            else str(last_message.content)
        )
        self.config.output_file.write(content)
