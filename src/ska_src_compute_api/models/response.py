from typing import Literal, Optional
from datetime import datetime, timedelta

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
    response_code: NonNegativeInt = Field(description="Response code; see README", examples=[2])
    response_text: str = Field(description="Response specification", examples=["1TB memory not bookable."])
    provision_id: Optional[str] = Field(description="Provision ID for claiming", examples=["24-surf-prov"])
    provision_validity: Optional[datetime] = Field(description="Validity of the provision",
                                                   example=datetime.now() + timedelta(minutes=10))

class JobSubmissionResponse(Response):
    response_code: NonNegativeInt = Field(description="Response code; see README", examples=[2])
    response_text: str = Field(description="Response specification",
                               examples=["Job cannot be executed: data not in this location."])
    job_id: Optional[str] = Field(description="Job ID for status info", examples=["24-surf-job"])

class JobStatusResponse(Response):
    response_code: NonNegativeInt = Field(description="Response code; see README", examples=[1])
    response_text: str = Field(description="Response specification", example=["Running..."])
    logging: str = Field(description="Job logging.",
                         example="step1 | WARNING: File format will be deprecated\nstep1 | INFO:     Running\n"
                                 "step1 | INFO:     Done\nstep2 | INFO:     Running")
    output_data: AnyHttpUrl = Field(description="Output data location.",
                                    examples=["https://drive.surf.nl/SKA_files/job_24/output_dir/"])