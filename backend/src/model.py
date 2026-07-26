from datetime import datetime
from pydantic import BaseModel


class Image(BaseModel):
    id: int
    name: str
    timestamp: datetime
    image_filepath: str
    gcode_filepath: str
    render_filepath: str

class SVG(BaseModel):
    id: int
    name: str
    timestamp: datetime
    svg_filepath: str
    gcode_filepath: str
    render_filepath: str

class SVGEditRequest(BaseModel):
    x_scale: float
    x_translate: float
    y_scale: float
    y_translate: float