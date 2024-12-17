from pydantic import BaseModel

class Cliente(BaseModel):
    id: str
    nombreCliente: str

class Producto(BaseModel):
    id: str
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
    metodoEntrega: str  # "entrega" o "recogida"
    fechaEntregaEstimada: str
