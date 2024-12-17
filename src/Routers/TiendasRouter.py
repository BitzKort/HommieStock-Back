from fastapi import APIRouter, HTTPException
from src.models.TiendaModels import Tienda
from src.Repository.mongodb import database
from src.schemas.TiendaSchemas import listTiendaSerializer
from bson import ObjectId
from src.Repository.redis import redis
import time

tiendaRouter = APIRouter()

db = database["tiendas"]
tag = "Tiendas"

# Listar todas las tiendas
@tiendaRouter.get("/tienda/all", tags=[tag])
async def getAllTiendas():
    start = time.time()

    # Intentar obtener las tiendas desde Redis
    tiendas = redis.json().get("tiendas", "$")

    if tiendas is None:
        # Si no están en Redis, obtenerlas desde MongoDB
        tiendas = listTiendaSerializer(db.find())
        # Guardar las tiendas en Redis para futuras consultas
        redis.json().set("tiendas", "$", tiendas)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return tiendas

# Traer una tienda por ID
@tiendaRouter.get("/tienda/{id}", tags=[tag])
async def getTienda(id: str):
    start = time.time()

    # Verificar si la tienda está en Redis
    tienda_cache = redis.json().get(f"tienda:{id}", "$")

    if tienda_cache is None:
        try:
            object_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID inválido.")
        
        # Obtener la tienda desde MongoDB
        tienda = db.find_one({"_id": object_id})

        if tienda is not None:
            tienda["_id"] = str(tienda["_id"])
            # Guardar la tienda individual en Redis para futuras consultas
            redis.json().set(f"tienda:{id}", "$", tienda)
        else:
            raise HTTPException(status_code=404, detail="Tienda no encontrada.")
        
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        tienda = tienda_cache
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return tienda


@tiendaRouter.put("/tienda/update/{id}", tags=[tag])
async def updateTienda(id: str, tienda: Tienda):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    # Convertir el horario de operación a un diccionario
    tienda.horarioOperacion = dict(tienda.horarioOperacion)
    
    # Actualizar la tienda en MongoDB
    result = db.update_one({"_id": object_id}, {"$set": dict(tienda)})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tienda no encontrada.")
    
    # Eliminar la caché de la tienda en Redis
    redis.json().delete(f"tienda:{id}", "$")
    redis.json().delete("tiendas", "$")

    return {"mensaje": "Tienda actualizada correctamente."}


@tiendaRouter.put("/tienda/soft-delete/{id}", tags=[tag])
async def sofTiendaDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    tienda = db.find_one({"_id": object_id})
    
    if tienda is None:
        raise HTTPException(status_code=404, detail="Tienda no encontrada.")
    
    # Actualizar el estado de la tienda a "eliminada" (lógica de eliminación)
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})

    # Eliminar la caché de la tienda en Redis
    redis.json().delete(f"tienda:{id}", "$")
    redis.json().delete("tiendas", "$")

    return {"mensaje": "Tienda eliminada lógicamente."}


@tiendaRouter.delete("/tienda/delete/all", tags=[tag])
async def delete_all_tiendas():
    # Eliminar todas las tiendas de la colección
    resultado = db.delete_many({})
    
    # Verificar si no se eliminaron tiendas
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay tiendas para eliminar.")
    
    # Eliminar la caché de todas las tiendas en Redis
    redis.json().delete("tiendas", "$")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} tiendas."}
