from pydantic import BaseModel

class Pedido(BaseModel):
    _id: str
    producto: str
    cantidad: int
    estadoEnvio: str
    fechaPedido: str

class Cliente(BaseModel):
    _id: str
    nombre: str
    direccion: str
    ciudad: str
    codPostal: str
    historialPedidos: list[Pedido]
    estado: int