import pytest
import os
from unittest.mock import patch
from dataclasses import dataclass
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from fabric_agent_action.llms import LLMProvider, LLMConfig, ProviderType, constants


@dataclass
class TestConfig:
    __test__ = False
    agent_provider: ProviderType = "openai"
    agent_model: str = "gpt-4"
    agent_temperature: float = 0.7
    fabric_provider: ProviderType = "anthropic"
    fabric_model: str = "claude-3"
    fabric_temperature: float = 0.5


@pytest.fixture
def mock_env():
    with patch.dict(
        os.environ,
        {
            constants.OPENAI_API_KEY: "test-openai-key",
            constants.ANTHROPIC_API_KEY: "test-anthropic-key",
            constants.OPENROUTER_API_KEY: "test-openrouter-key",
        },
    ):
        yield


@pytest.fixture
def llm_provider():
    return LLMProvider(TestConfig())


def test_get_llm_instance_openai(mock_env, llm_provider):
    config = LLMConfig(provider="openai", model="gpt-4", temperature=0.7)

    llm = llm_provider._get_llm_instance(config)

    assert isinstance(llm.llm, ChatOpenAI)
    assert llm.use_system_message is True
    assert llm.max_number_of_tools is None


def test_get_llm_instance_anthropic(mock_env, llm_provider):
    config = LLMConfig(provider="anthropic", model="claude-3", temperature=0.5)

    llm = llm_provider._get_llm_instance(config)

    assert isinstance(llm.llm, ChatAnthropic)
    assert llm.use_system_message is True
    assert llm.max_number_of_tools is None


def test_get_llm_instance_openrouter(mock_env, llm_provider):
    config = LLMConfig(provider="openrouter", model="gpt-4o", temperature=0.7)

    llm = llm_provider._get_llm_instance(config)

    assert isinstance(llm.llm, ChatOpenAI)
    assert llm.use_system_message is True
    assert llm.max_number_of_tools == 128


def test_get_llm_instance_special_model_config(mock_env, llm_provider):
    config = LLMConfig(provider="openai", model="openai/o1-preview", temperature=0.7)

    llm = llm_provider._get_llm_instance(config)

    assert isinstance(llm.llm, ChatOpenAI)
    assert llm.use_system_message is False
    assert llm.max_number_of_tools == 256


def test_get_llm_instance_invalid_provider(mock_env, llm_provider):
    config = LLMConfig(
        provider="invalid_provider", model="gpt-4", temperature=0.7  # type: ignore
    )

    with pytest.raises(ValueError, match="Unsupported provider: invalid_provider"):
        llm_provider._get_llm_instance(config)


def test_get_llm_instance_missing_api_key():
    # Create a clean environment without any API keys
    with patch.dict(os.environ, {}, clear=True):
        provider = LLMProvider(TestConfig())
        config = LLMConfig(provider="openai", model="gpt-4", temperature=0.7)

        with pytest.raises(SystemExit):
            provider._get_llm_instance(config)


def test_create_agent_llm(mock_env, llm_provider):
    llm = llm_provider.createAgentLLM()

    assert isinstance(llm.llm, ChatOpenAI)
    assert llm.use_system_message is True


def test_create_fabric_llm(mock_env, llm_provider):
    llm = llm_provider.createFabricLLM()

    assert isinstance(llm.llm, ChatAnthropic)
    assert llm.use_system_message is True


@pytest.mark.parametrize(
    "provider,model,expected_tools,expected_system_message",
    [
        ("openrouter", "gpt-4o", 128, True),
        ("openai", "openai/o1-preview", 256, False),
        ("openai", "gpt-4", None, True),
    ],
)
def test_model_configurations(
    mock_env, llm_provider, provider, model, expected_tools, expected_system_message
):
    config = LLMConfig(provider=provider, model=model, temperature=0.7)

    llm = llm_provider._get_llm_instance(config)

    assert llm.max_number_of_tools == expected_tools
    assert llm.use_system_message == expected_system_message
