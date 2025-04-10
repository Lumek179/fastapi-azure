from pydantic import BaseModel
from datetime import datetime

class Department(BaseModel):
    id: int
    department: str

    class Config:
        from_attributes = True

class Job(BaseModel):
    id: int
    job: str

    class Config:
        from_attributes = True

class HiredEmployee(BaseModel):
    id: int
    name: str
    datetime: datetime
    department_id: int
    job_id: int

    class Config:
        from_attributes = True
