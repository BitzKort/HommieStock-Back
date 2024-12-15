from fastapi import APIRouter, HTTPException
from src.models.DevolucionesModels import Devolucion
from src.Repository.mongodb import database
from src.schemas.DevolucioneSchemas import listDevolucionSerializer
from bson import ObjectId
devolucionRouter = APIRouter()

db = database["devoluciones"]

#Traer toda la lista de devoluciones
@devolucionRouter.get("/devolucion/all", tags=["Devoluciones"])
async def all():
    devoluciones = listDevolucionSerializer(db.find())
    return devoluciones

#Buscar devolución por ID
@devolucionRouter.get("/devolucion/{id}", tags=["Devoluciones"])
async def get_devolucion(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    devolucion = db.find_one({"_id": object_id})
    
    if devolucion is not None:
        devolucion["_id"] = str(devolucion["_id"])
        return devolucion

#Crear una devolución
@devolucionRouter.post("/devolucion/create", tags=["Devoluciones"])
async def create(devolucion: Devolucion):
    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    db.insert_one(dict(devolucion))
    
#Actualizar una devolución
@devolucionRouter.put("/devolucion/update/{id}", tags=["Devoluciones"])
async def update(id: str, devolucion: Devolucion):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    db.update_one({"_id": object_id}, {"$set": dict(devolucion)})
    
    return {"mensaje": "Devolución actualizada."}

#Borrado lógico de una devolución
@devolucionRouter.put("/devolucion/soft-delete/{id}", tags=["Devoluciones"])
async def soft_delete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    devolucion = db.find_one({"_id": object_id})
    
    if devolucion is None:
        raise HTTPException(status_code=404, detail="Devolución no encontrada.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Devolución eliminada."}\

#Borrar todas las devoluciones (para pruebas)
@devolucionRouter.delete("/devolucion/delete", tags=["Devoluciones"])
async def delete_all_devoluciones():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay devoluciones para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} devoluciones."}