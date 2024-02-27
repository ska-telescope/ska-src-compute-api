import json
from ska_src_compute_api.models import input
from datetime import datetime

def query_resources(json_doc: str) -> dict:
    my_num_cpu = 100
    my_current_cpu_avail = 40
    my_gpu = ["K40", "RX7900XT"]
    my_max_mem = 100000
    json_data = json.loads(json_doc)
    response_code, response_text = input.validate_model(json_data, input.QueryInput)
    if json_data['data_location'] != "Demo City":
        response_code = 4
        response_text = "Internal error. Could not connect to the database."
    availability = True
    unavail_msg = ""
    if not response_code:
        if json_data["cpu_cores"] > my_num_cpu:
            availability = False
            unavail_msg += "Number of requested CPU cores not available. "
        if json_data["gpu_model"] not in my_gpu:
            availability = False
            unavail_msg += f"{json_data['gpu_model']} GPU not available"
        if json_data['memory_mb'] > my_max_mem:
            availability = False
            unavail_msg += "Requested memory not available"
        if not availability:
            response_code = 1
            response_text = unavail_msg
    if not response_code:
        if json_data["cpu_cores"] > my_current_cpu_avail:
            availability = False
            unavail_msg = "Number of requested CPU cores not bookable."
        if not availability:
            response_code = 2
            response_text = unavail_msg

    return {"response_code": response_code, "response_text":response_text}
