from fastapi import APIRouter
from src.models.Tiendamodels import Tienda
from src.Repository.mongodb import database
from src.schemas.Tiendasschemas import listTiendaSerializer
tiendaRouter = APIRouter()

db = database["tiendas"]

@tiendaRouter.get("/tienda/all")
async def algo():

    tiendas = listTiendaSerializer(db.find())
    return tiendas

@tiendaRouter.post("/tienda/create")
async def create(tienda: Tienda):
    tienda.horarioOperacion = dict(tienda.horarioOperacion)
    db.insert_one(dict(tienda))