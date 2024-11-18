import pytest

from fabric_agent_action.app import app
from fabric_agent_action.config import AppConfig
from tests.integration.helpers import (
    fabric_patterns_included,
    helper_file_path,
    helper_read_output,
)


@pytest.mark.parametrize(
    "input_file_name,agent_type",
    [
        ("input_router_clean.txt", "router"),
        ("input_router_clean_improve_error.txt", "router"),
        ("input_react_clean_improve.txt", "react"),
        ("input_react_stride_threat_model_summary.txt", "react"),
        ("input_react_issue_clean_improve_step1.txt", "react_issue"),
        ("input_react_issue_clean_improve_step2.txt", "react_issue"),
        ("input_react_issue_stride_threat_model_summary_step1.txt", "react_issue"),
        ("input_react_issue_stride_threat_model_summary_step2.txt", "react_issue"),
        ("input_react_issue_stride_threat_model_summary_step3.txt", "react_issue"),
        ("input_react_pr_step1.txt", "react_pr"),
        ("input_react_pr_step2.txt", "react_pr"),
        ("input_react_pr_step3.txt", "react_pr"),
        ("input_react_pr_step4.txt", "react_pr"),
    ],
)
@pytest.mark.integration
def test_agent(input_file_name, agent_type):
    output_file_name = "result_" + input_file_name
    output_file = helper_file_path(output_file_name, "w")
    config = AppConfig(
        input_file=helper_file_path(input_file_name),
        output_file=output_file,
        agent_type=agent_type,
        fabric_patterns_included=fabric_patterns_included,
    )
    app(config)
    output = helper_read_output(output_file)
    assert output
    assert "no fabric pattern for this request" not in output
