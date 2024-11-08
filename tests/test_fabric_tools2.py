# test_fabric_tools.py
import pytest
import os
import tempfile
from fabric_agent_action.fabric_tools import FabricTools
import subprocess


@pytest.fixture(scope="module")
def echo_script():
    # Create a temporary directory and script
    temp_dir = tempfile.mkdtemp()
    script_path = os.path.join(temp_dir, "mock_script.sh")

    # Create script content based on OS
    if os.name == "nt":  # Windows
        script_content = "@echo off\n" "echo Command args: %*\n" "type %1"
        script_path = os.path.join(temp_dir, "mock_script.bat")
    else:  # Unix-like
        script_content = "#!/bin/bash\n" 'echo "Command args: $*"\n' 'cat "$1"'

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


class MockFabricTools(FabricTools):
    def run_fabric_command(self, input: str, pattern: str) -> str:
        # Create temporary file for input
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(input)
            temp_file_path = temp_file.name

        try:
            process = subprocess.Popen(
                [self.cmdPath, temp_file_path, "-p", pattern, "-m", self.model],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            stdout_data, stderr_data = process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Error executing '{self.cmdPath}': {stderr_data}")

            return stdout_data
        finally:
            try:
                os.unlink(temp_file_path)
            except (OSError, IOError) as e:
                print(f"Error removing temporary file: {e}")


@pytest.fixture(scope="module")
def fabric(echo_script):
    script_path = echo_script
    return MockFabricTools(cmdPath=script_path)


@pytest.mark.parametrize(
    "input_text",
    [
        "some input",
        "input with new lines\nnextline\nand another one",
        "input with special chars `like` this and \nmultiline",
    ],
)
def test_improve_writing_parametrized(fabric, input_text):
    result = fabric.improve_writing(input_text)
    print(f"Result: {result}")  # Debug print
    assert "Command args:" in result
    assert "-p improve_writing" in result
    assert input_text in result
