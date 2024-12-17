from pydantic import BaseModel


class Contactos(BaseModel):
    telefono: str
    email: str


class Proveedores(BaseModel):

    _id: str
    nombre: str
    precioCompra: int
    contacto: Contactos


class Producto(BaseModel):
    _id: str
    nombre: str
    descripcion: str
    numeroSerie: str
    categoria: str
    precioUnitario: int
    fechaCaducidad: str
    proveedores: list[Proveedores]
