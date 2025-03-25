from pydantic import BaseModel


class ThreadBase(BaseModel):
    mobile_number: str
    thread_id: str


class ThreadCreate(ThreadBase):
    pass


class ThreadResponse(ThreadBase):
    class Config:
        from_attributes = True
