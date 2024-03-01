from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime, timedelta


class Input(BaseModel):
    pass


class QueryInput(Input):
    class GPU(str, Enum):
        no_gpu = "none"
        K40 = "K40"
        A100 = "A100"
        RTX4090 = "RTX4090"
        RX7900XT = "RX7900XT"
    data_location: str = Field(examples=["surf"], description="Data location")
    data_size: int = Field(description="Input data size (in GB)", examples=[60000])
    output_data_size: int = Field(description="Output data size (in GB)", examples=[8000])
    memory: int = Field(description="Memory required (in GB)", examples=[196])
    cpu_cores: int = Field(description="Number of CPU cores required", examples=[16])
    runtime: int = Field(description="Expected runtime (in hours)", examples=[72])
    gpu_model: Optional[GPU] = Field(description="GPU model required", examples=["K40"])
    deadline: datetime = Field(description="Deadline for the processing", example=datetime.now() + timedelta(days=10))


