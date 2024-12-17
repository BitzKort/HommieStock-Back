from pydantic import BaseModel

class ProductoCompra(BaseModel):
    id_producto: str  # ID del producto comprado
    cantidad: int
    precio_unitario: float  # Precio de compra unitario

class Compra(BaseModel):
    _id: str
    proveedor_id: str  # ID del proveedor
    productos: list[ProductoCompra]
    fecha_compra: str
    total: float
    estado: str  # Ejemplo: "Pendiente", "Completado"