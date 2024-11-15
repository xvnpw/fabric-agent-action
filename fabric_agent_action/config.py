import io

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Literal


class AppConfig(BaseModel):
    """Configuration model with validation"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    input_file: io.TextIOWrapper
    output_file: io.TextIOWrapper
    verbose: bool = Field(default=False)
    debug: bool = Field(default=False)
    agent_provider: Literal["openai", "openrouter", "anthropic"] = Field(
        default="openai"
    )
    agent_model: str = Field(default="gpt-4")
    agent_temperature: float = Field(default=0, ge=0, le=1)
    agent_preamble_enabled: bool = Field(default=False)
    agent_preamble: str = Field(default="##### (🤖 AI Generated)")
    fabric_provider: Literal["openai", "openrouter", "anthropic"] = Field(
        default="openai"
    )
    fabric_model: str = Field(default="gpt-4")
    fabric_temperature: float = Field(default=0, ge=0, le=1)
    agent_type: Literal["single_command", "react"] = Field(default="single_command")
    fabric_max_num_turns: int = Field(default=10, gt=0)
    fabric_patterns_included: str
    fabric_patterns_excluded: str
