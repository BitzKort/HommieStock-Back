from pydantic import BaseModel


class horarioOperacion(BaseModel):
    
    horarioEntrada: str
    horarioSalida: str
    

class Tienda(BaseModel):
    _id: str
    nombre: str
    direccion: str
    ciudad: str
    codPostal: str
    capacidadAlmacenamiento: str
    horarioOperacion: horarioOperacion
    estado:int
    inventarios: list[str] #Hace referencia al id de un inventario de la coleccion de inventarios