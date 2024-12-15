from pydantic import BaseModel

class Pedido(BaseModel):
    _id: str
    producto: str
    cantidad: int
    estadoEnvio: str
    fechaPedido: str

class Devolucion(BaseModel):
    _id: str
    pedidoRe: list[Pedido]
    motivoDevolucion: str
    cantidadDevuelta: int
    fechaDevolucion: str
    estado: int
    