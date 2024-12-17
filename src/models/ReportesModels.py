from pydantic import BaseModel
from typing import Any

class Reporte (BaseModel):
    _id: str
    datos: Any


class ReporteProducto(BaseModel):
    idProducto:str
    nombreProducto: str
    stock:str
class ReporteInventarioTienda(BaseModel):
    idInventario: str
    producto:ReporteProducto


class ReporteStockTienda (BaseModel):
    _id: str
    idTienda: str
    inventariosTienda: list[ReporteInventarioTienda]
    stockTotal:str
