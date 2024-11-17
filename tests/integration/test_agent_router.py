import pytest

from fabric_agent_action.app import app
from fabric_agent_action.config import AppConfig
from tests.integration.helpers import fabric_patterns_included, helper_file_path


@pytest.mark.integration
def test_router_clean_text():
    """Test that should run only one tool and return result"""
    input_file_name = "input_router_clean.txt"
    config = AppConfig(
        input_file=helper_file_path(input_file_name),
        output_file=helper_file_path("result_" + input_file_name, "w"),
        fabric_patterns_included=fabric_patterns_included,
    )
    app(config)


@pytest.mark.integration
def test_router_clean_improve_error():
    """Test that should try to execute two tools and not one. Possibly can end with error"""
    input_file_name = "input_router_clean_improve_error.txt"
    config = AppConfig(
        input_file=helper_file_path(input_file_name),
        output_file=helper_file_path("result_" + input_file_name, "w"),
        fabric_patterns_included=fabric_patterns_included,
    )
    app(config)
