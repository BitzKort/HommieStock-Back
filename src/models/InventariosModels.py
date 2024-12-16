from pydantic import BaseModel

class Producto (BaseModel):
    id: str
    numeroSerie: str
    nombre: str
    categoria: str
    
class Inventario (BaseModel):
    _id: str
    productos: Producto
    ubicacionTienda: str #Hace referencia al id de una tienda de la coleccion de tiendas
    stock: int
    fechaLlegada: str
    fechaUltimaAct: str
    nivelAlertaReposicion: int