from pydantic import BaseModel


class Contacto(BaseModel):
    telefono: str
    email: str

class ProductoSuministrados(BaseModel):
    nombre: str
    precioCompra: int
    precioUnitario: int
    categoria: str


class Proveedores(BaseModel):

    nombre: str
    direccion: str
    ciudad: str
    codigoPostal: str
    contacto: Contacto
    productosSuministrados: list[ProductoSuministrados]
    estado: int