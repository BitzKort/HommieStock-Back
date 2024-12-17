from pydantic import BaseModel
from typing import Any

#Modelo para el crud de reporte
class Reporte (BaseModel):
    _id: str
    datos: Any

#modelos para reporte de stock total de tienda
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

class ReporteStockMain (BaseModel):
    _id: str
    datos: ReporteStockTienda

#Modelo para reporte del costo del inventario

    