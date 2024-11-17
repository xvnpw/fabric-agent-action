import pytest

from fabric_agent_action.app import app
from fabric_agent_action.config import AppConfig
from tests.integration.helpers import fabric_patterns_included, helper_file_path


@pytest.mark.integration
def test_react_clean_improve_text():
    """Test that should run only two tools: clean text and improve writing"""
    input_file_name = "input_react_clean_improve.txt"
    config = AppConfig(
        input_file=helper_file_path(input_file_name),
        output_file=helper_file_path("result_" + input_file_name, "w"),
        agent_type="react",
        fabric_patterns_included=fabric_patterns_included,
    )
    app(config)


@pytest.mark.integration
def test_react_stride_threat_model_summary():
    """Test that should run only two tools: create stride threat model and create summary of it"""
    input_file_name = "input_react_stride_threat_model_summary.txt"
    config = AppConfig(
        input_file=helper_file_path(input_file_name),
        output_file=helper_file_path("result_" + input_file_name, "w"),
        agent_type="react",
        fabric_patterns_included=fabric_patterns_included,
    )
    app(config)
