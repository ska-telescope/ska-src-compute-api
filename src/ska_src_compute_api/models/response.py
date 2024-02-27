from typing import Literal
from datetime import datetime

from pydantic import BaseModel, Field, NonNegativeInt, AnyHttpUrl


class Response(BaseModel):
    pass


class GenericErrorResponse(Response):
    detail: str


class GenericOperationResponse(Response):
    successful: bool = Field(examples=[True])


class HealthResponse(Response):
    class DependentServices(BaseModel):
        class DependentServiceStatus(BaseModel):
            status: Literal["UP", "DOWN"] = Field(examples=["UP"])
        permissions_api: DependentServiceStatus = Field(alias="permissions-api")
    uptime: NonNegativeInt = Field(examples=[1000])
    number_of_managed_requests: NonNegativeInt = Field(examples=[50])
    dependent_services: DependentServices


class PingResponse(Response):
    status: Literal["UP", "DOWN"]
    version: str

class QueryResponse(Response):
    response_code: NonNegativeInt = Field(examples=[1])
    response_text: str = Field(examples=["10 CPUs and K100 not available."])

class ProvisionResponse(Response):
    response_code: NonNegativeInt = Field(examples=[2])
    response_text: str = Field(examples=["1TB memory not bookable."])
    provision_id: str = Field(examples=["24-surf-prov"])
    provision_validity: datetime

class JobStatusResponse(Response):
    response_code: NonNegativeInt = Field(examples=[1])
    response_text: str = Field(example=["Running..."])
    logging: str = "step1 | WARNING: File format will be deprecated\nstep1 | INFO:     Running\n"\
                   "step1 | INFO:     Done\nstep2 | INFO:     Running"
    output_data: AnyHttpUrl = Field(examples=["https://drive.surf.nl/SKA_files/job_24/output_dir/"])