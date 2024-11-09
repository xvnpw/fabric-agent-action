import argparse
import sys
import os
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from fabric_agent_action import constants
from fabric_tools import FabricTools

logger = logging.getLogger(__name__)


def main():
    args = parse_arguments()

    openai_api_key = os.environ.get(constants.OPENAI_API_KEY)
    if not openai_api_key:
        print(f"{constants.OPENAI_API_KEY} not set in env")
        sys.exit(1)

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

    fabricTools = FabricTools(cmdPath=args.fabric_path)

    graph = build_graph(fabricTools)
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
        "-f", "--fabric-path", type=str, default="fabric", help="Path to fabric binary"
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
    return parser.parse_args()


def build_graph(fabricTools):
    logger.debug("building graph...")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm_with_tools = llm.bind_tools(fabricTools.get_fabric_tools())

    sys_msg = SystemMessage(
        content="""You are a fabric assistant, that is tasked to run actions using fabric tools on given input. 
        
        I will send you input and you should pick right fabric tool for my request. If you are unable to decide on fabric pattern return "no fabric pattern for this request" and finish.
        """
    )

    def assistant(state):
        return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(fabricTools.get_fabric_tools()))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", END)
    graph = builder.compile()

    return graph


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
