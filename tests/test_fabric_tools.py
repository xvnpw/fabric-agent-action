import pytest
import os
import tempfile
from fabric_agent_action.fabric_tools import FabricTools


@pytest.fixture(scope="module")
def echo_script():
    # Create a temporary directory and echo script
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, "echo_script.sh")

    # Create script content based on OS
    if os.name == "nt":  # Windows
        script_content = (
            "@echo off\n"
            "set /p stdin=\n"
            "echo Command args: %*\n"
            "echo Input: %stdin%"
        )
        script_path = os.path.join(temp_dir, "echo_script.bat")
    else:  # Unix-like
        script_content = (
            "#!/bin/bash\n"
            "read -r stdin\n"
            'printf "Command args: %s\\n" "$*"\n'
            'printf "Input: %s\\n" "$stdin"'
        )

    # Write the script
    with open(script_path, "w") as f:
        f.write(script_content)

    # Make the script executable on Unix-like systems
    if os.name != "nt":
        os.chmod(script_path, 0o755)

    yield script_path

    # Cleanup after tests
    try:
        os.remove(script_path)
        os.rmdir(temp_dir)
    except (OSError, IOError) as e:
        print(f"Error during cleanup: {e}")


@pytest.fixture(scope="module")
def fabric(echo_script):
    return FabricTools(cmdPath=echo_script)


@pytest.fixture(scope="module")
def bad_command():
    # Create a temporary non-executable file
    temp_dir = tempfile.mkdtemp()
    bad_cmd = os.path.join(temp_dir, "non_executable")
    with open(bad_cmd, "w") as f:
        f.write("dummy")

    yield bad_cmd

    # Cleanup
    try:
        os.remove(bad_cmd)
        os.rmdir(temp_dir)
    except (OSError, IOError) as e:
        print(f"Error during cleanup: {e}")


@pytest.mark.parametrize(
    "input_text", ["some input", "yet another input", "inte`restring` input"]
)
def test_improve_writing_parametrized(fabric, input_text):
    result = fabric.improve_writing(input_text)
    assert input_text in result
    assert "-p improve_writing" in result


def test_error_handling(bad_command):
    fabric_bad = FabricTools(cmdPath=bad_command)
    with pytest.raises(OSError):
        fabric_bad.improve_writing("test")


def test_custom_model(echo_script):
    custom_model = "custom-model"
    fabric = FabricTools(cmdPath=echo_script, model=custom_model)
    result = fabric.improve_writing("test input")
    assert f"-m {custom_model}" in result
