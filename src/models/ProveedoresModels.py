from pydantic import BaseModel

class Contacto(BaseModel):
    telefono: str
    email: str

class ProductoSuministrados(BaseModel):
    id: str
    nombre: str
    precioCompra: int
    precioUnitario: int
    categoria: str

class TerminoEntrega(BaseModel):
    plazo: str  # Ejemplo: "5 días hábiles"
    metodo: str  # Ejemplo: "Transporte terrestre"

class CondicionPago(BaseModel):
    plazo: str  # Ejemplo: "30 días"
    metodo: str  # Ejemplo: "Transferencia bancaria"

class Proveedores(BaseModel):
    nombre: str
    direccion: str
    ciudad: str
    codigoPostal: str
    contacto: Contacto
    productosSuministrados: list[ProductoSuministrados]
    terminoEntrega: TerminoEntrega
    condicionPago: CondicionPago
    estado: int