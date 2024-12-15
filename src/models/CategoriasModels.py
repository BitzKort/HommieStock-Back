from pydantic import BaseModel

class Producto(BaseModel):
    _id: str
    nombre: str
    descripcion: str

class Categoria(BaseModel):
    nombre: str
    descripcion: str
    productos: list[Producto]
    estado: int