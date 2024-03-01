from sqlalchemy.orm import Session
import ska_src_compute_api.database.models as db_models
from datetime import datetime, timedelta
from ska_src_compute_api import models as api_models

def add_provision(db: Session, provision_data: api_models.QueryInput, user_id):
    provision = db_models.Provisions(validity=datetime.now()+timedelta(minutes=10),
                                     user_id=user_id, data_location=provision_data.data_location,
                                     data_size=provision_data.data_size,
                                     output_data_size=provision_data.output_data_size, memory=provision_data.memory,
                                     cpu_cores=provision_data.cpu_cores, runtime=provision_data.runtime,
                                     gpu_model=provision_data.gpu_model)
    db.add(provision)
    db.commit()
    db.refresh(provision)
    return provision

def add_job(db:Session, provision: db_models.Provisions):
    job = db_models.Jobs(provision = provision.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
