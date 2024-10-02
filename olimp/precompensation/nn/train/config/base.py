from pydantic import BaseModel


class StrictModel(BaseModel):
    """
    This class exists to not allow extra keys
    """

    class Config:
        extra = "forbid"
