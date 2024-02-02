from typing import Literal

from pydantic import BaseModel, Field, NonNegativeInt


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
