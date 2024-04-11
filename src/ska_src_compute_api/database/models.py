from ska_src_compute_api.database.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, PickleType


class Provisions(Base):
    __tablename__ = "provisions"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    validity = Column(DateTime)
    data_location = Column(String)
    data_size = Column(Integer)
    output_data_size = Column(Integer)
    memory = Column(Integer)
    cpu_cores = Column(Integer)
    runtime = Column(Integer)
    gpu_model = Column(String, nullable=True)


class Jobs(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    container = Column(String)
    params = Column(PickleType)
    dataset = Column(String)
    contact_email = Column(String, nullable=True)
    provision = Column(Integer, ForeignKey("provisions.id"))


class JobStatus(Base):
    __tablename__ = "jobstatus"
    id = Column(Integer, primary_key=True)
    flow = Column(String)
    flow_stage = Column(Integer)
    job = Column(Integer, ForeignKey("jobs.id"))
