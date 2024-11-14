import argparse
import io
import logging
import sys
from typing import Optional, TextIO

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from typing_extensions import Literal

from fabric_agent_action.agents import AgentBuilder
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


class AppConfig(BaseModel):
    """Configuration model with validation"""

    input_file: io.TextIOWrapper
    output_file: io.TextIOWrapper
    verbose: bool = Field(default=False)
    debug: bool = Field(default=False)
    agent_provider: Literal["openai", "openrouter", "anthropic"] = Field(
        default="openai"
    )
    agent_model: str = Field(default="gpt-4")
    agent_temperature: float = Field(default=0, ge=0, le=1)
    agent_preamble_enabled: bool = Field(default=False)
    agent_preamble: str = Field(default="##### (🤖 AI Generated)")
    fabric_provider: Literal["openai", "openrouter", "anthropic"] = Field(
        default="openai"
    )
    fabric_model: str = Field(default="gpt-4")
    fabric_temperature: float = Field(default=0, ge=0, le=1)
    agent_type: Literal["single_command", "react"] = Field(default="single_command")
    fabric_max_num_turns: int = Field(default=10, gt=0)
    fabric_patterns_included: Optional[str] = None
    fabric_patterns_excluded: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


def setup_logging(verbose: bool, debug: bool) -> None:
    """Configure logging based on verbosity levels"""
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    elif verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(level=logging.WARNING)


def read_input(input_file: TextIO) -> str:
    """Read input from file or stdin with proper error handling"""
    try:
        return input_file.read()
    except (KeyboardInterrupt, EOFError):
        logger.error("Input reading interrupted")
        raise SystemExit("No input provided. Exiting.")
    except Exception as e:
        logger.error(f"Error reading input: {e}")
        raise


def parse_arguments() -> AppConfig:
    """Parse command line arguments and return AppConfig"""
    logger.debug("Setting up argument parser...")

    parser = argparse.ArgumentParser(description="Fabric Agent Action CLI")

    # Input/Output arguments
    io_group = parser.add_argument_group("Input/Output Options")
    io_group.add_argument(
        "-i",
        "--input-file",
        type=argparse.FileType("r"),
        required=True,
        help="Input file",
    )
    io_group.add_argument(
        "-o",
        "--output-file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default: stdout)",
    )

    # Logging arguments
    log_group = parser.add_argument_group("Logging Options")
    log_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    log_group.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    # Agent configuration
    agent_group = parser.add_argument_group("Agent Configuration")
    agent_group.add_argument(
        "--agent-provider",
        type=str,
        choices=["openai", "openrouter", "anthropic"],
        default="openai",
        help="LLM provider for agent (default: openai)",
    )
    agent_group.add_argument(
        "--agent-model",
        type=str,
        default="gpt-4o",
        help="Model name for agent (default: gpt-4o)",
    )
    agent_group.add_argument(
        "--agent-temperature",
        type=float,
        default=0,
        help="Sampling temperature for agent model (default: 0)",
    )
    agent_group.add_argument(
        "--agent-type",
        type=str,
        choices=["single_command", "react"],
        default="single_command",
        help="Type of agent (default: single_command)",
    )
    agent_group.add_argument(
        "--agent-preamble-enabled",
        action="store_true",
        help="Enable preamble in output",
    )
    agent_group.add_argument(
        "--agent-preamble",
        type=str,
        default="##### (🤖 AI Generated)",
        help="Preamble added to the beginning of output (default: ##### (🤖 AI Generated)",
    )

    # Fabric configuration
    fabric_group = parser.add_argument_group("Fabric Configuration")
    fabric_group.add_argument(
        "--fabric-provider",
        type=str,
        choices=["openai", "openrouter", "anthropic"],
        default="openai",
        help="LLM provider for fabric (default: openai)",
    )
    fabric_group.add_argument(
        "--fabric-model",
        type=str,
        default="gpt-4o",
        help="Model name for fabric (default: gpt-4o)",
    )
    fabric_group.add_argument(
        "--fabric-temperature",
        type=float,
        default=0,
        help="Sampling temperature for fabric model (default: 0)",
    )
    fabric_group.add_argument(
        "--fabric-patterns-included",
        type=str,
        help="Comma separated list of fabric patterns to include in agent",
    )
    fabric_group.add_argument(
        "--fabric-patterns-excluded",
        type=str,
        help="Comma separated list of fabric patterns to exclude in agent",
    )
    fabric_group.add_argument(
        "--fabric-max-num-turns",
        type=int,
        default=10,
        help="Maximum number of turns to LLM when running fabric patterns (default: 10)",
    )

    args = parser.parse_args()

    config = AppConfig(**vars(args))

    return config


def main() -> None:
    try:
        config = parse_arguments()
        setup_logging(config.verbose, config.debug)

        logger.info("Starting Fabric Agent Action")

        input_str = read_input(config.input_file)

        llm_provider = LLMProvider(config)
        fabric_llm = llm_provider.createFabricLLM()
        fabric_tools = FabricTools(
            fabric_llm.llm,
            fabric_llm.use_system_message,
            fabric_llm.max_number_of_tools,
            config.fabric_patterns_included,
            config.fabric_patterns_excluded,
        )

        agent_builder = AgentBuilder(config.agent_type, llm_provider, fabric_tools)
        graph = agent_builder.build()

        executor = GraphExecutor(config)
        executor.execute(graph, input_str)

        logger.info("Fabric Agent Action completed successfully")

    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    finally:
        # Ensure files are properly closed
        if "config" in locals():
            if config.input_file and config.input_file is not sys.stdin:
                config.input_file.close()
            if config.output_file and config.output_file is not sys.stdout:
                config.output_file.close()


class GraphExecutor:
    def __init__(self, config: AppConfig):
        self.config = config
        self._setup_output_encoding()

    def _setup_output_encoding(self) -> None:
        if isinstance(self.config.output_file, io.TextIOWrapper):
            try:
                self.config.output_file.reconfigure(encoding="utf-8")
            except Exception as e:
                logger.warning(
                    f"Could not set UTF-8 encoding: {e}. Falling back to system default."
                )

    def execute(self, graph, input_str: str) -> None:
        try:
            messages_state = self._invoke_graph(graph, input_str)

            for msg in messages_state["messages"]:
                logger.debug(f"Message: {msg.pretty_repr()}")

            self._write_output(messages_state)
        except Exception as e:
            logger.error(f"Graph execution failed: {str(e)}")
            raise

    def _invoke_graph(self, graph, input_str: str) -> dict:
        input_messages = [HumanMessage(content=input_str)]
        return graph.invoke(
            {
                "messages": input_messages,
                "max_num_turns": self.config.fabric_max_num_turns,
            }
        )

    def _write_output(self, messages_state: dict) -> None:
        last_message = messages_state["messages"][-1]
        if not isinstance(last_message, AIMessage) or not last_message.content:
            raise ValueError("Invalid or empty AI message")

        content = self._format_output(last_message.content)
        self.config.output_file.write(content)

    def _format_output(self, content: str) -> str:
        return (
            f"{self.config.agent_preamble}\n\n{content}"
            if self.config.agent_preamble_enabled
            else content
        )


if __name__ == "__main__":
    main()
