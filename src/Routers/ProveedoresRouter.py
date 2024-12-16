import time
from fastapi import APIRouter, HTTPException
from src.models.ProveedoresModels import Proveedores, Contacto, ProductoSuministrados
from src.Repository.mongodb import database
from src.schemas.ProveedoreSchemas import listproveedoreSerializer
from bson import ObjectId
from src.Repository.redis import redis

proveedorRouter = APIRouter()

db = database["proveedores"]

# Traer toda la lista de proveedores
@proveedorRouter.get("/proveedor/all")
async def getAllProveedor():
    start = time.time()

    # Intentamos obtener los proveedores desde Redis
    proveedor = redis.json().get("proveedores", "$")

    if proveedor is None:
        # Si no están en Redis, los obtenemos desde MongoDB
        proveedor = listproveedoreSerializer(db.find())
        # Guardamos los proveedores en Redis para futuras consultas
        redis.json().set("proveedores", "$", proveedor)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return proveedor


# Buscar proveedor por ID
@proveedorRouter.get("/proveedor/{id}")
async def getProveedor(id: str):
    try:
        # Intentamos convertir el id a un ObjectId válido
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Primero intentamos buscar el proveedor en Redis
    proveedor = redis.json().get(f"proveedor:{id}", "$")

    if proveedor is None:
        # Si no está en Redis, buscamos en la base de datos
        proveedor = db.find_one({"_id": object_id})

        if proveedor is None:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
        
        # Convertimos el _id de ObjectId a string antes de devolverlo
        proveedor["_id"] = str(proveedor["_id"])

        # Guardamos el proveedor en Redis para futuras consultas
        redis.json().set(f"proveedor:{id}", "$", proveedor)
    
    return proveedor


@proveedorRouter.post("/proveedor/create")

async def create(proveedor: Proveedores):

    proveedor.contacto = dict(proveedor.contacto)
    proveedor.productosSuministrados = [dict(p) for p in proveedor.productosSuministrados]
    db.insert_one(dict(proveedor))


@proveedorRouter.put("/proveedor/update/{id}")

async def updateProveedor(id: str, proveedor: Proveedores):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor.contacto = dict(proveedor.contacto)
    proveedor.productosSuministrados = [dict(p) for p in proveedor.productosSuministrados]
    db.update_one({"_id": object_id}, {"$set": dict(proveedor)})
    
    return {"mensaje": "proveedor actualizado."}



@proveedorRouter.put("/proveedor/soft-delete/{id}")

async def softProveedorDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor = db.find_one({"_id": object_id})
    
    if proveedor is None:
        raise HTTPException(status_code=404, detail="proveedor no encontrado.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "proveedor eliminado."}

@proveedorRouter.delete("/proveedor/delete/all")

async def deleteAllProvedoores():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay proveedores para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} proveedores."}