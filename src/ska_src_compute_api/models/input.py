from pydantic import BaseModel, ValidationError
from typing import Optional
from enum import Enum
from datetime import datetime


def validate_model(data, model):
    output_code = 0
    output_text = "OK"
    try:
        model.model_validate(json_data)
    except ValidationError as val_err:
        output_code = 3
        output_text = "Input can not be validated. Errors: "
        for error_object in val_err.errors():
            output_text += f"{error_object['loc'][0]}: {error_object['msg']}; "
    return output_code, output_text.rstrip(", ")


class Input(BaseModel):
    pass


class QueryInput(Input):
    class GPU(str, Enum):
        no_gpu = "none"
        K40 = "K40"
        A100 = "A100"
        RTX4090 = "RTX4090"
        RX7900XT = "RX7900XT"
    data_location: str
    data_size: int
    output_data_size: int
    memory: int
    cpu_cores: int
    runtime: int
    gpu_model: Optional[GPU]
    deadline: datetime


