from fastapi import APIRouter, HTTPException
from src.models.DevolucionesModels import Devolucion
from src.Repository.mongodb import database
from src.schemas.DevolucioneSchemas import listDevolucionSerializer
from bson import ObjectId
devolucionRouter = APIRouter()

db = database["devoluciones"]

import time
from fastapi import APIRouter, HTTPException
from src.models.DevolucionesModels import Devolucion
from src.Repository.mongodb import database
from src.schemas.DevolucioneSchemas import listDevolucionSerializer
from bson import ObjectId
from src.Repository.redis import redis

devolucionRouter = APIRouter()

db = database["devoluciones"]

# Traer toda la lista de devoluciones
@devolucionRouter.get("/devolucion/all")
async def all():
    start = time.time()

    devoluciones = redis.json().get("devoluciones", "$")

    if devoluciones is None:
        devoluciones = listDevolucionSerializer(db.find())
        # Guardamos en Redis
        redis.json().set("devoluciones", "$", devoluciones)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return devoluciones


# Buscar devolución por ID
@devolucionRouter.get("/devolucion/{id}")
async def get_devolucion(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Primero intentamos buscar en Redis
    devolucion = redis.json().get(f"devolucion:{id}", "$")

    if devolucion is None:
        # Si no está en Redis, buscamos en la base de datos
        devolucion = db.find_one({"_id": object_id})

        if devolucion is None:
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")
        
        # Convertir el _id de ObjectId a string para devolverlo de forma correcta
        devolucion["_id"] = str(devolucion["_id"])

        # Guardamos la devolución en Redis para futuras consultas
        redis.json().set(f"devolucion:{id}", "$", devolucion)
    
    return devolucion


#Crear una devolución
@devolucionRouter.post("/devolucion/create")
async def create(devolucion: Devolucion):
    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    db.insert_one(dict(devolucion))
    
#Actualizar una devolución
@devolucionRouter.put("/devolucion/update/{id}")
async def update(id: str, devolucion: Devolucion):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    db.update_one({"_id": object_id}, {"$set": dict(devolucion)})
    
    return {"mensaje": "Devolución actualizada."}

#Borrado lógico de una devolución
@devolucionRouter.put("/devolucion/soft-delete/{id}")
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
@devolucionRouter.delete("/devolucion/delete")
async def delete_all_devoluciones():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay devoluciones para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} devoluciones."}