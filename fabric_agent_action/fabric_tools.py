import subprocess


class FabricTools:
    def __init__(self, cmdPath="fabric", model="gpt-4o"):
        self.model = model
        self.cmdPath = cmdPath

    def improve_writing(self, input: str):
        """Improves writing of input text using fabric pattern

        Args:
            input: input text to improve writing
        """
        return self.run_fabric_command(input, "improve_writing")

    def create_stride_threat_model(self, input: str):
        """Create STRIDE threat model for given design document using fabric pattern

        Args:
            input: input document for STRIDE threat modeling
        """
        return self.run_fabric_command(input, "create_stride_threat_model")

    def create_summary(self, input: str):
        """Create summary of given document using fabric pattern

        Args:
            input: document to create summary
        """
        return self.run_fabric_command(input, "create_summary")

    def create_quiz(self, input: str):
        """Generates questions to help student review the main concepts of the leaning objectives using fabric pattern

        Args:
            input: subject and/or list of learning objectives
        """
        return self.run_fabric_command(input, "create_quiz")

    def run_fabric_command(self, input, pattern):
        process = subprocess.Popen(
            [self.cmdPath, "-p", pattern, "-m", self.model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        stdout_data, stderr_data = process.communicate(input=input)

        if process.returncode != 0:
            raise RuntimeError(f"Error executing 'fabric': {stderr_data}")

        return stdout_data

    def get_fabric_tools(self) -> list:
        return [
            self.create_stride_threat_model,
            self.create_summary,
            self.create_quiz,
            self.improve_writing,
        ]
