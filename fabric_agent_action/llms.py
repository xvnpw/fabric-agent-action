import logging
import os
import sys
from dataclasses import dataclass
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from fabric_agent_action import constants

logger = logging.getLogger(__name__)

ProviderType = Literal["openrouter", "openai", "anthropic"]


@dataclass
class LLMConfig:
    provider: ProviderType
    model: str
    temperature: float


class LLMProvider:
    def __init__(self, config):
        self.config = config
        self._provider_configs = {
            "openrouter": {
                "env_key": constants.OPENROUTER_API_KEY,
                "api_base": constants.OPENROUTER_API_BASE,
                "class": ChatOpenAI,
            },
            "openai": {
                "env_key": constants.OPENAI_API_KEY,
                "api_base": None,
                "class": ChatOpenAI,
            },
            "anthropic": {
                "env_key": constants.ANTHROPIC_API_KEY,
                "api_base": None,
                "class": ChatAnthropic,
            },
        }

    def _get_llm_instance(self, llm_config: LLMConfig) -> tuple[BaseChatModel, bool]:
        """
        Create an LLM instance based on the provided configuration.
        Returns a tuple of (LLM instance, use_system_message flag)
        """
        provider_config = self._provider_configs.get(llm_config.provider)
        if not provider_config:
            raise ValueError(f"Unsupported provider: {llm_config.provider}")

        # Check if API key is set
        api_key = os.environ.get(provider_config["env_key"])
        if not api_key:
            print(f"{provider_config['env_key']} not set in env")
            sys.exit(1)

        # Determine if system messages should be used
        use_system_message = "o1-preview" not in llm_config.model

        if not use_system_message:
            logger.debug(
                f"[{llm_config.provider}] use system message disabled for model: {llm_config.model}"
            )

        # Log configuration
        logger.debug(
            f"using {llm_config.provider} provider with model={llm_config.model}"
        )

        # Create kwargs for LLM initialization
        kwargs = {
            "temperature": llm_config.temperature,
            "model_name": llm_config.model,
            "api_key": api_key,
        }

        # Add api_base for OpenRouter
        if provider_config["api_base"]:
            kwargs["openai_api_base"] = provider_config["api_base"]

        return provider_config["class"](**kwargs), use_system_message

    def createAgentLLM(self) -> tuple[BaseChatModel, bool]:
        return self._get_llm_instance(
            LLMConfig(
                provider=self.config.agent_provider,
                model=self.config.agent_model,
                temperature=self.config.agent_temperature,
            )
        )

    def createFabricLLM(self) -> tuple[BaseChatModel, bool]:
        return self._get_llm_instance(
            LLMConfig(
                provider=self.config.fabric_provider,
                model=self.config.fabric_model,
                temperature=self.config.fabric_temperature,
            )
        )
