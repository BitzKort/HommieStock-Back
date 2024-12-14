from fastapi import APIRouter
from src.models.Clientesmodels import Cliente
from src.Repository.mongodb import database
from src.schemas.Clienteschemas import listClienteSerializer
clienteRouter = APIRouter()

db = database["clientes"]

@clienteRouter.get("/cliente/all")
async def all():
    clientes = listClienteSerializer(db.find())
    return clientes

@clienteRouter.post("/cliente/create")
async def create(cliente: Cliente):    
    cliente.historialPedidos = [dict(p) for p in cliente.historialPedidos]
    db.insert_one(dict(cliente))