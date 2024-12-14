from pydantic import BaseModel

class Cliente(BaseModel):
    _id: str
    nombreCliente: str

class Producto(BaseModel):
    numeroSerie: str
    cantidad: int
    nombre: str
    precioUnitario: float

class Pedido(BaseModel):
    _id: str
    cliente: Cliente
    productos: list[Producto]
    precioTotal: float
    estado: str
    fechaPedido: str

