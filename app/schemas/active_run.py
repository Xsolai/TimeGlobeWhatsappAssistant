from pydantic import BaseModel


class ActiveRunBase(BaseModel):
    thread_id: str
    run_id: str


class ActiveRunCreate(ActiveRunBase):
    """Schema for creating an active run."""

    pass


class ActiveRunResponse(ActiveRunBase):
    """Schema for returning an active run."""

    class Config:
        from_attributes = True  # Allows ORM model conversion
