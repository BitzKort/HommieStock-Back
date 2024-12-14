from fastapi import APIRouter
from src.models.Devolucionesmodels import Devolucion
from src.Repository.mongodb import database
from src.schemas.Devolucionesschemas import listDevolucionSerializer
devolucionRouter = APIRouter()

db = database["devoluciones"]

@devolucionRouter.get("/devolucion/all")
async def all():
    devoluciones = listDevolucionSerializer(db.find())
    return devoluciones

@devolucionRouter.post("/devolucion/create")
async def create(devolucion: Devolucion):
    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    db.insert_one(dict(devolucion))