from ska_src_compute_api.models import (
    QueryInput,
    QueryResponse,
    ProvisionResponse,
    JobInput,
    JobSubmissionResponse,
    JobStatusResponse,
)
from datetime import datetime, timedelta
from ska_src_compute_api.database import crud, models
from ska_src_compute_api.database.database import engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)


def query_resources(query_input: QueryInput) -> QueryResponse:
    my_num_cpu = 100
    my_current_cpu_avail = 40
    my_gpu = ["K40", "RX7900XT"]
    my_max_mem = 100
    response_code, response_text = 0, "Ok"
    if query_input.data_location != "democity":
        response_code = 3
        response_text = "Internal error. Could not connect to the database."
        return QueryResponse.parse_obj(
            {"response_code": response_code, "response_text": response_text}
        )
    availability = True
    unavail_msg = ""
    if query_input.cpu_cores > my_num_cpu:
        availability = False
        unavail_msg += "Number of requested CPU cores not available. "
    if query_input.gpu_model not in my_gpu:
        availability = False
        unavail_msg += f"{query_input.gpu_model} GPU not available"
    if query_input.memory > my_max_mem:
        availability = False
        unavail_msg += "Requested memory not available"
    if not availability:
        response_code = 1
        response_text = unavail_msg
        return QueryResponse.parse_obj(
            {"response_code": response_code, "response_text": response_text}
        )
    if (
        query_input.cpu_cores > my_current_cpu_avail
        and query_input.deadline < datetime.now() + timedelta(days=5)
    ):
        availability = False
        unavail_msg = "Number of requested CPU cores not bookable."
    if not availability:
        response_code = 2
        response_text = unavail_msg
    return QueryResponse.parse_obj(
        {"response_code": response_code, "response_text": response_text}
    )


def provision_resources(provision_input: QueryInput, db: Session, user_id: str):
    availability = query_resources(provision_input)
    if availability.response_code:
        return availability
    provision = crud.add_provision(db, provision_input, user_id)
    my_site = "demo.city"
    provision_ref = f"{my_site}-{provision.id}.prov"
    return ProvisionResponse.parse_obj(
        {
            "response_code": availability.response_code,
            "response_text": availability.response_text,
            "provision_id": provision_ref,
            "provision_validity": provision.validity,
        }
    )


def submit_job(job_input: JobInput, provision_id: str, db: Session, user_id: str):
    my_site = "demo.city"
    job = crud.add_job(
        job_data=job_input,
        provision_id=provision_id,
        db=db,
        data_centre=my_site,
        user_id=user_id,
    )
    if job:
        return JobSubmissionResponse.parse_obj(job)


def job_status(provision_id: str, db: Session, user_id: str):
    current_job_status = crud.get_job_status(
        db=db, provision_id=provision_id, user_id=user_id
    )
    return JobStatusResponse.parse_obj(current_job_status)
