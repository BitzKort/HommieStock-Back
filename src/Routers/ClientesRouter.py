import json
from fastapi import APIRouter, HTTPException
from src.models.ClientesModels import Cliente
from src.Repository.mongodb import database
from src.schemas.ClienteSchemas import listClienteSerializer
from bson import ObjectId
from src.Repository.redis import redis
import time

clienteRouter = APIRouter()

db = database["clientes"]


# Traer todos los clientes
@clienteRouter.get("/cliente/all")
async def all():
    start = time.time()

    clientes = redis.json().get("clientes", "$")

    if clientes is None:
        clientes = listClienteSerializer(db.find())
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
        redis.json().set("clientes", "$", clientes)
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return clientes


# Crear un cliente
@clienteRouter.post("/cliente/create")
async def create(cliente: Cliente):
    cliente.historialPedidos = [dict(p) for p in cliente.historialPedidos]
    db.insert_one(dict(cliente))


# Actualizar un cliente
@clienteRouter.put("/cliente/update/{id}")
async def update(id: str, cliente: Cliente):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    cliente.historialPedidos = [dict(p) for p in cliente.historialPedidos]
    db.update_one({"_id": object_id}, {"$set": dict(cliente)})

    return {"mensaje": "Cliente actualizado."}


# Borrado lógico de un cliente
@clienteRouter.put("/cliente/soft-delete/{id}")
async def soft_delete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    cliente = db.find_one({"_id": object_id})

    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")

    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})

    return {"mensaje": "Cliente eliminado."}


# Borrar todas los clientes (para pruebas)
@clienteRouter.delete("/cliente/delete")
async def delete_all_clientes():
    resultado = db.delete_many({})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay clientes para eliminar.")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} clientes."}
