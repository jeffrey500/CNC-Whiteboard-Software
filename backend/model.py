from datetime import datetime

from pydantic import BaseModel

class Image(BaseModel):
    id: int
    name: str
    timestamp: datetime
    image_url: str

    def __init__(self, id: int, name: str, timestamp: str, image_url: str, **kwargs):
        # transform or compute values before validation

        # Forward parameters to Pydantic's internal initialization
        super().__init__(id=id, name=name, timestamp=timestamp, image_url=image_url, **kwargs)
