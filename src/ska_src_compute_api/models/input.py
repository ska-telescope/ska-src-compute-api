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

    data_location: str = Field(examples=["democity"], description="Data location")
    data_size: int = Field(description="Input data size (in GB)", examples=[60000])
    output_data_size: int = Field(
        description="Output data size (in GB)", examples=[8000]
    )
    memory: int = Field(description="Memory required (in GB)", examples=[196])
    cpu_cores: int = Field(description="Number of CPU cores required", examples=[16])
    runtime: int = Field(description="Expected runtime (in hours)", examples=[72])
    gpu_model: Optional[GPU] = Field(description="GPU model required", examples=["K40"])
    deadline: datetime = Field(
        description="Deadline for the processing",
        example=datetime.now() + timedelta(days=10),
    )


class JobInput(Input):
    container: str = Field(
        examples=["astroimaging/sourcefinder:3.4"],
        description="Reference to the container to run the job in.",
    )
    dataset: str = Field(
        examples=["https://webdav.data.skao.int/3811823/dataproduct.fits"],
        description="Reference to the data set to perform the processing on",
    )
    params: Optional[dict] = Field(
        examples=[{"--gaussians": "True", "--maxiter": 1000, "--minsnr": "10"}],
        description="Runtime options for the command to execute in the container.",
    )
    contact_email: Optional[str] = Field(
        examples=["jdoe@astro.demouniversity.org"],
        description="email address for notiffications about the job.",
    )
