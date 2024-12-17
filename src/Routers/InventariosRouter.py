from fastapi import APIRouter, HTTPException
from src.models.InventariosModels import Inventario
from src.Repository.mongodb import database
from src.schemas.InventariosSchemas import listInventarioSerializer
from bson import ObjectId
from src.Repository.redis import redis

inventarioRouter = APIRouter()

dbInventarios = database["inventarios"]
tag = "Inventarios"


# Listar todos los inventarios
@inventarioRouter.get("/inventario/all", tags=[tag])
async def getAllInventarios():
    inventarios = redis.json().get("inventarios", "$")

    if inventarios is None:
        inventarios = listInventarioSerializer(dbInventarios.find())
        redis.json().set("inventarios", "$", inventarios)

    return inventarios


# Traer un inventario por id
@inventarioRouter.get("/inventario/{id}", tags=[tag])
async def getInventarios(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    inventario = redis.json().get(f"inventario:{id}", "$")

    if inventario is None:
        inventario = dbInventarios.find_one({"_id": object_id})
        if inventario is None:
            raise HTTPException(status_code=404, detail="Inventario no encontrado.")

        inventario["_id"] = str(inventario["_id"])
        redis.json().set(f"inventario:{id}", "$", inventario)

    return inventario


# Listar inventarios por id de las tiendas
@inventarioRouter.get("/inventario/tienda/{id}", tags=[tag])
async def getInventarioByTienda(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    inventarios = redis.json().get(f"inventario:tienda:{id}", "$")

    if inventarios is None:
        inventarios_cursor = dbInventarios.find({"ubicacionTienda": id})
        inventarios = [Inventario(**documento) for documento in inventarios_cursor]
        inventarios_dict = [inventario.model_dump() for inventario in inventarios]

        redis.json().set(f"inventario:tienda:{id}", "$", inventarios_dict)

    return inventarios


# Crear un inventario
@inventarioRouter.post("/inventario/create", tags=[tag])
async def createInventario(inventario: Inventario):
    inventario = inventario.model_dump()
    dbInventarios.insert_one(inventario)
    redis.delete("inventarios")
    redis.delete("tiendas")
    return {"mensaje": "Inventario creado correctamente."}


# Actualizar un inventario
@inventarioRouter.put("/inventario/update/{id}", tags=[tag])
async def update(id: str, inventario_update: Inventario):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    inventario_update = inventario_update.model_dump()

    result = dbInventarios.update_one({"_id": object_id}, {"$set": inventario_update})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Inventario no encontrado.")

    redis.delete(f"inventario:{id}")
    redis.delete("inventarios")

    return {"mensaje": "Inventario actualizado correctamente."}


# Borrar logicamente un inventario
@inventarioRouter.put("/inventario/soft-delete/{id}", tags=[tag])
async def softDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    inventario = dbInventarios.find_one({"_id": object_id})

    if inventario is None:
        raise HTTPException(status_code=404, detail="Inventario no encontrado.")

    dbInventarios.update_one({"_id": object_id}, {"$set": {"estado": 0}})

    redis.delete(f"inventario:{id}")
    redis.delete("inventarios")

    return {"mensaje": "Inventario eliminado correctamente (soft delete)."}
