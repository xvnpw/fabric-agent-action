import argparse
import logging
import sys

from langchain_core.messages import HumanMessage

from fabric_agent_action.agents import AgentBuilder
from fabric_agent_action.fabric_tools import FabricTools
from fabric_agent_action.llms import LLMProvider

logger = logging.getLogger(__name__)


def main():
    args = parse_arguments()

    if args.verbose is True:
        logging.basicConfig(level=logging.INFO)

    if args.debug is True:
        logging.basicConfig(level=logging.DEBUG)

    try:
        if args.input_file:
            input_str = args.input_file.read()
        else:
            input_str = sys.stdin.read()
    except (KeyboardInterrupt, EOFError):
        print("\nNo input provided. Exiting.")
        return

    llm_provider = LLMProvider(args)

    fabric_llm, use_system_message = llm_provider.createFabricLLM()
    fabric_tools = FabricTools(fabric_llm, use_system_message)

    agent_builder = AgentBuilder(args.agent_type, llm_provider, fabric_tools)

    graph = agent_builder.build()
    invoke(graph, input_str, args.output_file)


def parse_arguments() -> argparse.Namespace:
    logger.debug("setting up parser...")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (default is stdin)",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default is stdout)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="turn on verbose messages, default: false",
        default="false",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="turn on debug messages, default: false",
        default="false",
    )
    parser.add_argument(
        "--agent-provider",
        type=str,
        choices=["openai", "openrouter"],
        help="name of LLM provider for agent, default: openai",
        default="openai",
    )
    parser.add_argument(
        "--agent-model",
        type=str,
        help="name model for agent, default: gpt-4o",
        default="gpt-4o",
    )
    parser.add_argument(
        "--agent-temperature",
        type=float,
        help="sampling temperature for agent model, default 0",
        default=0,
    )
    parser.add_argument(
        "--fabric-provider",
        type=str,
        choices=["openai", "openrouter"],
        help="name of LLM provider for fabric, default: openai",
        default="openai",
    )
    parser.add_argument(
        "--fabric-model",
        type=str,
        help="name model for fabric, default: gpt-4o",
        default="gpt-4o",
    )
    parser.add_argument(
        "--fabric-temperature",
        type=float,
        help="sampling temperature for fabric model, default 0",
        default=0,
    )
    parser.add_argument(
        "--agent-type",
        type=str,
        choices=["single_command", "react"],
        help="type of agent, default: single_command",
        default="single_command",
    )
    return parser.parse_args()


def invoke(graph, input_str, output_file):
    logger.debug("invoking graph...")

    input_messages = [HumanMessage(content=input_str)]

    messagesState = graph.invoke({"messages": input_messages})

    logger.debug("graph invoked")

    for m in messagesState["messages"]:
        logger.debug("message: " + m.pretty_repr())

    last_message = messagesState["messages"][-1]
    output_file.write(last_message.content)


if __name__ == "__main__":
    main()
