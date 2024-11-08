import argparse
import sys
import os
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from fabric_agent_action import constants
from fabric_tools import FabricTools


openai_api_key = os.environ.get(constants.OPENAI_API_KEY)
if not openai_api_key:
    print(f"{constants.OPENAI_API_KEY} not set in env")
    sys.exit(1)


def main():
    args = parse_arguments()

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
    return parser.parse_args()


def build_graph(fabricTools):
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
    input_messages = [HumanMessage(content=input_str)]

    messagesState = graph.invoke({"messages": input_messages})

    for m in messagesState["messages"]:
        output_file.write(m.pretty_repr() + "\n")


if __name__ == "__main__":
    main()
