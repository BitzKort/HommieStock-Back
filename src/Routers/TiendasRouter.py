from fastapi import APIRouter, HTTPException
from src.models.TiendaModels import Tienda
from src.Repository.mongodb import database
from src.schemas.TiendaSchemas import listTiendaSerializer
from bson import ObjectId

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

@tiendaRouter.get("/tienda/all")

async def getAll():
    
    tienda = listTiendaSerializer(db.find())
    return tienda

@tiendaRouter.get("/tienda/{id}")

async def getTienda(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    tienda = db.find_one({"_id": object_id})
    
    if tienda is not None:
        tienda["_id"] = str(tienda["_id"])
        return tienda

@tiendaRouter.put("/tienda/update/{id}")

async def updateTienda(id: str, tienda: Tienda):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    tienda.horarioOperacion = [dict(p) for p in tienda.horarioOperacion]
    db.update_one({"_id": object_id}, {"$set": dict(tienda)})
    
    return {"mensaje": "tienda actualizada."}


@tiendaRouter.put("/tienda/soft-delete/{id}")

async def softDeleteTienda():
    
    pass

@tiendaRouter.delete("tienda/delete/all")

async def delete_all_tiendas():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay tiendas para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} tiendas."}