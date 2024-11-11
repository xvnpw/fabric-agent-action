import argparse
import logging
import sys
from dataclasses import dataclass
from typing import TextIO

from langchain_core.messages import HumanMessage

from fabric_agent_action.agents import AgentBuilder
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Configuration class to hold application settings"""

    input_file: TextIO
    output_file: TextIO
    verbose: bool
    debug: bool
    agent_provider: str
    agent_model: str
    agent_temperature: float
    fabric_provider: str
    fabric_model: str
    fabric_temperature: float
    agent_type: str
    fabric_tools_include: str
    fabric_tools_exclude: str


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
        default=sys.stdin,
        help="Input file (default: stdin)",
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
        "--fabric-tools-include",
        type=str,
        help="Comma separated list of fabric tools to include in agent",
    )
    fabric_group.add_argument(
        "--fabric-tools-exclude",
        type=str,
        help="Comma separated list of fabric tools to exclude in agent",
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
            fabric_llm.number_of_tools,
            config.fabric_tools_include,
            config.fabric_tools_exclude,
        )

        agent_builder = AgentBuilder(config.agent_type, llm_provider, fabric_tools)
        graph = agent_builder.build()

        invoke_graph(graph, config, input_str, config.output_file)

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


def invoke_graph(graph, config, input_str: str, output_file: TextIO) -> None:
    logger.debug("Invoking graph...")

    try:
        input_messages = [HumanMessage(content=input_str)]
        messages_state = graph.invoke({"messages": input_messages})

        logger.debug("Graph execution completed")

        for msg in messages_state["messages"]:
            logger.debug(f"Message: {msg.pretty_repr()}")

        last_message = messages_state["messages"][-1]

        content = f"# (AI Generated, provider: {config.fabric_provider}, model: {config.fabric_model})\n\n{last_message.content}"

        output_file.write(content)

    except Exception as e:
        logger.error(f"Error during graph execution: {e}")
        raise


if __name__ == "__main__":
    main()
