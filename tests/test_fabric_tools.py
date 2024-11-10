import pytest
from langchain_core.language_models.fake_chat_models import ParrotFakeChatModel

from fabric_agent_action.fabric_tools import FabricTools


@pytest.fixture(scope="module")
def llm():
    return ParrotFakeChatModel()


def test_read_fabric_patterns(llm):
    fabric_tools = FabricTools(llm)
    pattern = fabric_tools.read_fabric_pattern("create_quiz")
    assert len(pattern) > 0


def test_read_fabric_pattern_on_not_exist(llm):
    fabric_tools = FabricTools(llm)
    with pytest.raises(OSError):
        fabric_tools.read_fabric_pattern("not_exists")


def test_invoke_llm(llm):
    fabric_tools = FabricTools(llm)
    fabric_output = fabric_tools.invoke_llm(
        "create quiz for me about hammer", "create_quiz"
    )
    assert "create quiz for me about hammer" in fabric_output
