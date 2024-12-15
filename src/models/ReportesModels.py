from pydantic import BaseModel
from typing import Any

class Reporte (BaseModel):
    id: str
    datos: Any
