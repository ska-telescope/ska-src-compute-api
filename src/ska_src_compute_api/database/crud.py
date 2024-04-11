from sqlalchemy.orm import Session
from typing import Optional, Dict, Union
import ska_src_compute_api.database.models as db_models
from datetime import datetime, timedelta
from ska_src_compute_api import models as api_models
import re


def add_provision(
    db: Session, provision_data: api_models.QueryInput, user_id: str
) -> db_models.Provisions:
    provision = db_models.Provisions(
        validity=datetime.now() + timedelta(minutes=10),
        user_id=user_id,
        data_location=provision_data.data_location,
        data_size=provision_data.data_size,
        output_data_size=provision_data.output_data_size,
        memory=provision_data.memory,
        cpu_cores=provision_data.cpu_cores,
        runtime=provision_data.runtime,
        gpu_model=provision_data.gpu_model,
    )
    db.add(provision)
    db.commit()
    db.refresh(provision)
    return provision


def get_provision(provision_id: int, db: Session) -> Optional[db_models.Provisions]:
    provision = db.query(db_models.Provisions).filter(db_models.Provisions.id == provision_id).first()  # type: ignore
    if not provision:
        return None
    return provision


def check_provision_validity(
    provision: db_models.Provisions, db: Session
) -> Optional[bool]:
    return datetime.now() <= provision.validity


def parse_provision_id(provision_id: str) -> Union[Dict[str, Union[str, int]], int]:
    try:
        prov_id = re.match(".*-(\d+).prov", provision_id).group(1)
    except AttributeError:
        return {
            "response_code": 2,
            "response_text": "Invalid provision: Provision format is invalid.",
            "job_id": None,
        }
    return prov_id


def add_job(
    db: Session,
    job_data: api_models.JobInput,
    provision_id: str,
    data_centre: str,
    user_id: str,
) -> Dict[str, Union[str, int]]:
    prov_id = parse_provision_id(provision_id)
    provision = get_provision(prov_id, db)
    provcheck = check_provision_validity(provision, db)
    if provision.user_id != user_id:
        return {"response_code": 4, "response_text": "Access denied", "job_id": None}
    if not any(value in job_data.dataset for value in ["/demo_city/", "skao.int"]):
        return {
            "response_code": 1,
            "response_text": "Job cannot be executed: Data not in this location",
            "job_id": None,
        }
    if provcheck is None:
        return {
            "response_code": 2,
            "response_text": "Invalid provision: Provision ID unknown.",
            "job_id": None,
        }
    if not provcheck:
        return {
            "response_code": 2,
            "response_text": "Invalid provision: Provision expired.",
            "job_id": None,
        }
    job = db_models.Jobs(
        provision=prov_id,
        user_id=user_id,
        container=job_data.container,
        params=job_data.params,
        dataset=job_data.dataset,
        contact_email=job_data.contact_email,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    if "--fail" in job.params.keys():
        job_flow = "fail_flow"
    elif "--error" in job.params.keys():
        job_flow = "error_flow"
    else:
        job_flow = "happy_flow"
    job_status = db_models.JobStatus(job=job.id, flow=job_flow, flow_stage=0)
    db.add(job_status)
    db.commit()
    job_id = f"{data_centre}-{job.id}.job"
    return {"response_code": 1, "response_text": "Ok", "job_id": job_id}


flows = {
    "happy_flow": [
        [
            1,
            "Running...",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources",
            None,
        ],
        [
            1,
            "Running...",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources\n"
            "Found 18 sources\nDone\nStep 2/2: Creating catalogue...",
            None,
        ],
        [
            0,
            "OK",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources\n"
            "Found 18 sources\nDone\nStep 2/2: Creating catalogue...\nCatalogue successfully created",
            "http://webdav.datastore.skao.int/surveyKSP/catalogue.dat",
        ],
    ],
    "fail_flow": [
        [
            1,
            "Running...",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources",
            None,
        ],
        [
            5,
            "Execution error: Application crashed",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources\n"
            "Step 2/2: Creating catalogue...\nWriting catalogue failed: access denied",
            None,
        ],
    ],
    "error_flow": [
        [
            1,
            "Running...",
            "Step 1/2: Source finder\nFound 10 sources\nFound 15 sources",
            None,
        ],
        [
            6,
            "System error: System rebooted during run",
            "Step 1/2: Source finder\nFound 10 sources\n",
            None,
        ],
    ],
}


def get_job_status(
    db: Session, provision_id: str, user_id: str
) -> Dict[str, Union[str, int]]:
    prov_id = parse_provision_id(provision_id)
    job = db.query(db_models.Jobs).filter(db_models.Jobs.provision == prov_id).first()  # type: ignore
    if not job:
        return {"response_code": 2, "response_text": "Invalid job: Job does not exist"}
    if job.user_id != user_id:
        return {"response_code": 4, "response_text": "Access denied"}
    job_status = (
        db.query(db_models.JobStatus).filter(db_models.JobStatus.job == job.id).first()
    )
    job_flow = job_status.flow
    try:
        state = flows[job_flow][job_status.flow_stage]
    except IndexError:
        state = flows[job_flow][-1]
    else:
        job_status.flow_stage += 1
        db.commit()
        db.refresh(job_status)

    return dict(
        zip(["response_code", "response_text", "logging", "output_data"], state)
    )
