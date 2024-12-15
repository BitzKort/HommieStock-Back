from pydantic import BaseModel

class Tienda (BaseModel):
    id: str
    direccion: str
    ciudad: str
    codPostal: str

class Producto (BaseModel):
    id: str
    numeroSerie: str
    nombre: str
    categoria: str
    ubicacionTienda: list[Tienda]
    stock: int
    fechaLlegada: str
    fechaUltimaAct: str
    nivelAlertaReposicion: int

class Inventario (BaseModel):
    id: str
    productos: list[Producto]