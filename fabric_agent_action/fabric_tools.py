import logging
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class FabricTools:
    """Manages fabric patterns and their execution"""

    def __init__(self, llm: BaseChatModel, use_system_message: bool = True):
        self.llm = llm
        self.use_system_message = use_system_message
        self._patterns_cache: dict[str, str] = {}

    def read_fabric_pattern(self, pattern_name: str) -> str:
        """Read and cache fabric pattern content"""
        if pattern_name in self._patterns_cache:
            return self._patterns_cache[pattern_name]

        root_project_dir = Path(__file__).resolve().parent.parent
        patterns_folder = root_project_dir / "prompts/fabric_patterns"
        file_path = patterns_folder / pattern_name / "system.md"

        logger.debug(f"Reading fabric pattern from: {file_path}")

        try:
            with open(file_path, "r") as file:
                content = file.read()
            self._patterns_cache[pattern_name] = content
            return content
        except FileNotFoundError:
            logger.error(f"Pattern file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading pattern file: {e}")
            raise

    def invoke_llm(self, input: str, pattern_name: str) -> str:
        """Invoke LLM with proper error handling"""
        try:
            fabric_pattern = self.read_fabric_pattern(pattern_name)

            logger.debug(
                f"Invoking LLM with pattern={pattern_name}, "
                f"system_message={self.use_system_message}, "
                f"input_preview={input[:50]}..."
            )

            message_class = SystemMessage if self.use_system_message else HumanMessage
            messages = [
                message_class(content=fabric_pattern),
                HumanMessage(content=input),
            ]

            response = self.llm.invoke(messages)

            logger.debug(f"LLM response preview: {response.content[:50]}...")
            return response.content

        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            raise

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
