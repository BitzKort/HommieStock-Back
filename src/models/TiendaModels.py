from pydantic import BaseModel

class horarioOperacion(BaseModel):
    
    horarioEntrada: str
    horarioSalida: str
    

class Tienda(BaseModel):
    nombre: str
    direccion: str
    ciudad: str
    codPostal: str
    capacidadAlmacenamiento: str
    horarioOperacion: horarioOperacion