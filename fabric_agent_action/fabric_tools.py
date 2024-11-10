import logging
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class FabricTools:
    def __init__(self, llm: BaseChatModel, use_system_message=True):
        self.llm = llm
        self.use_system_message = use_system_message

    def read_fabric_pattern(self, pattern_name: str) -> str:
        # Construct the path to the file relative to the script location

        root_project_dir = Path(__file__).resolve().parent.parent
        logger.debug(
            f"looking for patterns starting with project root directory: {root_project_dir}"
        )

        patterns_folder = root_project_dir / "prompts/fabric_patterns"

        logger.debug(f"looking for fabric pattern in: {patterns_folder}")

        file_path = patterns_folder / pattern_name / "system.md"

        logger.debug(f"reading {pattern_name} from {file_path}...")

        with open(file_path, "r") as file:
            content = file.read()
        return content

    def invoke_llm(self, input: str, pattern_name: str) -> str:
        fabric_pattern = self.read_fabric_pattern(pattern_name)

        logger.debug(
            f"invoking llm with system message={self.use_system_message}, fabric pattern={pattern_name}, and input={input[:20]}..."
        )

        if self.use_system_message:
            message = self.llm.invoke(
                [SystemMessage(content=fabric_pattern)] + [HumanMessage(content=input)]
            )
        else:
            message = self.llm.invoke(
                [HumanMessage(content=fabric_pattern)] + [HumanMessage(content=input)]
            )

        logger.debug(f"got result from llm={message.content[:20]}...")

        return message.content

    def improve_writing(self, input: str):
        """Improves writing of input text using fabric pattern

        Args:
            input: input text to improve writing
        """
        return self.invoke_llm(input, "improve_writing")

    def create_stride_threat_model(self, input: str):
        """Create STRIDE threat model for given design document using fabric pattern

        Args:
            input: input document for STRIDE threat modeling
        """
        return self.invoke_llm(input, "create_stride_threat_model")

    def create_summary(self, input: str):
        """Create summary of given document using fabric pattern

        Args:
            input: document to create summary
        """
        return self.invoke_llm(input, "create_summary")

    def create_quiz(self, input: str):
        """Generates questions to help student review the main concepts of the leaning objectives using fabric pattern

        Args:
            input: subject and/or list of learning objectives
        """
        return self.invoke_llm(input, "create_quiz")

    def get_fabric_tools(self) -> list:
        return [
            self.create_stride_threat_model,
            self.create_summary,
            self.create_quiz,
            self.improve_writing,
        ]
