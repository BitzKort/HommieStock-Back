from pydantic import BaseModel
from typing import Any

class Reporte (BaseModel):
    _id: str
    datos: Any
