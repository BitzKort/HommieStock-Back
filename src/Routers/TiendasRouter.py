import time
from fastapi import APIRouter, HTTPException
from src.models.TiendaModels import Tienda
from src.Repository.mongodb import database
from src.schemas.TiendaSchemas import listTiendaSerializer
from bson import ObjectId
from src.Repository.redis import redis

tiendaRouter = APIRouter()

db = database["tiendas"]

# Traer toda la lista de tiendas
@tiendaRouter.get("/tienda/all")
async def getAllTiendas():
    start = time.time()

    # Intentamos obtener las tiendas desde Redis
    tiendas = redis.json().get("tiendas", "$")

    if tiendas is None:
        # Si no están en Redis, las obtenemos desde MongoDB
        tiendas = listTiendaSerializer(db.find())
        # Guardamos las tiendas en Redis para futuras consultas
        redis.json().set("tiendas", "$", tiendas)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return tiendas


# Buscar tienda por ID
@tiendaRouter.get("/tienda/{id}")
async def getTienda(id: str):
    try:
        # Intentamos convertir el id a un ObjectId válido
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Primero intentamos buscar la tienda en Redis
    tienda = redis.json().get(f"tienda:{id}", "$")

    if tienda is None:
        # Si no está en Redis, buscamos en la base de datos
        tienda = db.find_one({"_id": object_id})

        if tienda is None:
            raise HTTPException(status_code=404, detail="Tienda no encontrada.")
        
        # Convertimos el _id de ObjectId a string antes de devolverlo
        tienda["_id"] = str(tienda["_id"])

        # Guardamos la tienda en Redis para futuras consultas
        redis.json().set(f"tienda:{id}", "$", tienda)
    
    return tienda


@tiendaRouter.post("/tienda/create")
async def create(tienda: Tienda):
    tienda.horarioOperacion = dict(tienda.horarioOperacion)
    db.insert_one(dict(tienda))


@tiendaRouter.put("/tienda/update/{id}")

async def updateTienda(id: str, tienda: Tienda):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    tienda.horarioOperacion = dict(tienda.horarioOperacion)
    db.update_one({"_id": object_id}, {"$set": dict(tienda)})
    
    return {"mensaje": "tienda actualizada."}

@tiendaRouter.put("/tienda/soft-delete/{id}")

async def sofTiendaDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    tienda = db.find_one({"_id": object_id})
    
    if tienda is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Tienda eliminada."}

@tiendaRouter.delete("/tienda/delete/all")

async def delete_all_tiendas():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay tiendas para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} tiendas."}