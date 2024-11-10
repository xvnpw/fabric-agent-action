import logging
import os
import sys

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from fabric_agent_action import constants

logger = logging.getLogger(__name__)


class LLMProvider:
    def __init__(self, args):
        self.args = args

    def createAgentLLM(self) -> tuple[BaseChatModel, bool]:
        use_system_message = True
        if "o1-preview" in self.args.agent_model:
            logger.debug(
                f"[agent] use system message disabled for model: {self.args.agent_model}"
            )
            use_system_message = False

        if self.args.agent_provider == "openrouter":
            logger.debug(
                f"[agent] using openrouter provider with model={self.args.agent_model}"
            )
            openai_api_key = os.environ.get(constants.OPENROUTER_API_KEY)
            if not openai_api_key:
                print(f"{constants.OPENROUTER_API_KEY} not set in env")
                sys.exit(1)
            openai_api_base = constants.OPENROUTER_API_BASE

            return (
                ChatOpenAI(
                    temperature=self.args.agent_temperature,
                    model_name=self.args.agent_model,
                    openai_api_key=openai_api_key,
                    openai_api_base=openai_api_base,
                ),
                use_system_message,
            )
        elif self.args.agent_provider == "openai":
            logger.debug(
                f"[agent] using openai provider with model={self.args.agent_model}"
            )
            openai_api_key = os.environ.get(constants.OPENAI_API_KEY)
            if not openai_api_key:
                print(f"{constants.OPENAI_API_KEY} not set in env")
                sys.exit(1)

            return (
                ChatOpenAI(
                    temperature=self.args.agent_temperature,
                    model_name=self.args.agent_model,
                    openai_api_key=openai_api_key,
                ),
                use_system_message,
            )

    def createFabricLLM(self) -> tuple[BaseChatModel, bool]:
        use_system_message = True
        if "o1-preview" in self.args.fabric_model:
            logger.debug(
                f"[fabric] use system message disabled for model: {self.args.fabric_model}"
            )
            use_system_message = False

        if self.args.fabric_provider == "openrouter":
            logger.debug(
                f"[fabric] using openrouter provider with model={self.args.fabric_model}"
            )
            openai_api_key = os.environ.get(constants.OPENROUTER_API_KEY)
            if not openai_api_key:
                print(f"{constants.OPENROUTER_API_KEY} not set in env")
                sys.exit(1)
            openai_api_base = constants.OPENROUTER_API_BASE

            return (
                ChatOpenAI(
                    temperature=self.args.fabric_temperature,
                    model_name=self.args.fabric_model,
                    openai_api_key=openai_api_key,
                    openai_api_base=openai_api_base,
                ),
                use_system_message,
            )
        elif self.args.fabric_provider == "openai":
            logger.debug(
                f"[fabric] using openai provider with model={self.args.fabric_model}"
            )
            openai_api_key = os.environ.get(constants.OPENAI_API_KEY)
            if not openai_api_key:
                print(f"{constants.OPENAI_API_KEY} not set in env")
                sys.exit(1)

            return (
                ChatOpenAI(
                    temperature=self.args.fabric_temperature,
                    model_name=self.args.fabric_model,
                    openai_api_key=openai_api_key,
                ),
                use_system_message,
            )
