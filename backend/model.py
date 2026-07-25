from datetime import datetime
from pydantic import BaseModel


class Image(BaseModel):
    id: int
    name: str
    timestamp: datetime
    image_filepath: str
    gcode_filepath: str
    render_filepath: str
