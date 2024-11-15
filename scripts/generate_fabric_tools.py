from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def scan_folders(root_path):
    # Convert string path to Path object if needed
    root = Path(root_path)

    # Check if the root path exists
    if not root.exists():
        print(f"Error: Path {root_path} does not exist")
        return

    patterns = []

    # Iterate through all subdirectories
    for folder in root.iterdir():
        if folder.name in ["find_logical_fallacies"]:  # skipping
            continue
        if folder.is_dir():
            system_file = folder / "system.md"

            # Check if system.md exists in the subfolder
            if system_file.exists():
                try:
                    # Read the first 50 characters from the file
                    with open(system_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    patterns.append((folder.name, content))
                except Exception as e:
                    print(f"\nFolder: {folder.name}")
                    print(f"Error reading file: {str(e)}")
            else:
                print(f"\nFolder: {folder.name}")
                print("No system.md file found")

    return patterns


def create_tool_code(pattern_name, pattern_content, output_file):
    llm = ChatOpenAI(model="gpt-4o")

    sys_msg = SystemMessage(
        content="""You are a helpful assistant tasked with creating python functions that will be used as fabric tools for LLM. I will give you PROMPT NAME and PROMPT CONTENT. You will create me well formatted python function.

        FORMATTING

        def function_name(self, input: str) -> str:
            \"""Tool description

            Args:
                input: input text
            \"""
        return self.invoke_llm(input, "prompt_name")

        - replace function_name with value of PROMPT_NAME
        - prompt_name replace with value of PROMPT_NAME
        - description of tool must contains information that tool is "fabric pattern"

        EXAMPLE

        - PROMPT NAME: clean_text
        - PROMPT CONTENT: # IDENTITY and PURPOSE

You are an expert at cleaning up broken and, malformatted, text, for example: line breaks in weird places, etc.

# Steps

- Read the entire document and fully understand it.
- Remove any strange line breaks that disrupt formatting.
- Add capitalization, punctuation, line breaks, paragraphs and other formatting where necessary.
- Do NOT change any content or spelling whatsoever.

# OUTPUT INSTRUCTIONS

- Output the full, properly-formatted text.
- Do not output warnings or notes—just the requested sections.

# INPUT:

INPUT:

        - TOOL DESCRIPTION: Clean input text from broken and, malformatted text using fabric pattern
        """
    )

    human_msg = HumanMessage(
        content=f"PROMPT NAME: {pattern_name}\n\nPROMPT CONTENT: {pattern_content}\n\nTOOL DESCRIPTION:\n"
    )

    response = llm.invoke([sys_msg, human_msg])

    content = response.content
    if content:
        content = content.replace("```python", "")
        content = content.replace("```", "")

    output_file.write(content + "\n")


def convert_to_method(patterns: list) -> str:
    # Create the method signature
    result = "def get_fabric_tools(self) -> list:\n"
    result += "    return [\n"

    # Convert each pattern to self.pattern format
    formatted_items = [
        f"        self.{pattern_name}" for pattern_name, pattern_content in patterns
    ]

    # Join items with commas and new lines
    result += ",\n".join(formatted_items)

    # Close the list and function
    result += "\n    ]"

    return result


def convert_to_test(patterns: list) -> str:
    # Create the method signature
    result = "@pytest.mark.parametrize(\n"
    result += '    "pattern_name",\n'
    result += "    [\n"

    # Convert each pattern to self.pattern format
    formatted_items = [
        f'        "{pattern_name}"' for pattern_name, pattern_content in patterns
    ]

    # Join items with commas and new lines
    result += ",\n".join(formatted_items)

    # Close the list and function
    result += "\n    ],"
    result += "\n)"

    return result


if __name__ == "__main__":
    folder_path = "prompts/fabric_patterns"
    patterns = scan_folders(folder_path)

    if not patterns:
        print("No patterns found or error occurred while scanning folders.")
        exit(1)

    with open("fabric_tools.txt", "w", encoding="utf-8") as f:
        print(f"\nFound {len(patterns)} patterns:")
        for p, c in patterns:
            print(f"- {p}")
            create_tool_code(p, c, f)

        get_fabric_tools_str = convert_to_method(patterns)
        f.write(get_fabric_tools_str)

        p_test = convert_to_test(patterns)
        f.write(p_test)
