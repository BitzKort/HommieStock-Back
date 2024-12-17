from fastapi import APIRouter, HTTPException
from src.models.ProveedoresModels import Proveedores, Contacto, ProductoSuministrados
from src.Repository.mongodb import database
from src.schemas.ProveedoreSchemas import listproveedoreSerializer
from bson import ObjectId
from src.Repository.redis import redis
import time

proveedorRouter = APIRouter()

db = database["proveedores"]
tag = "Proveedores"

# Traer todos los proveedores
@proveedorRouter.get("/proveedor/all", tags=[tag])
async def getAllProveedor():
    start = time.time()

    # Intentar obtener los proveedores desde Redis
    proveedores = redis.json().get("proveedores", "$")

    if proveedores is None:
        # Si no están en Redis, obtenerlos desde MongoDB
        proveedores = listproveedoreSerializer(db.find())
        # Guardar los proveedores en Redis para futuras consultas
        redis.json().set("proveedores", "$", proveedores)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return proveedores

# Traer un proveedor por ID
@proveedorRouter.get("/proveedor/{id}", tags=[tag])
async def getProveedor(id: str):
    start = time.time()

    # Verificar si el proveedor está en Redis
    proveedor_cache = redis.json().get(f"proveedor:{id}", "$")

    if proveedor_cache is None:
        try:
            object_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID inválido.")
        
        # Obtener el proveedor desde MongoDB
        proveedor = db.find_one({"_id": object_id})

        if proveedor is not None:
            proveedor["_id"] = str(proveedor["_id"])
            # Guardar el proveedor individual en Redis para futuras consultas
            redis.json().set(f"proveedor:{id}", "$", proveedor)
        else:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
        
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        proveedor = proveedor_cache
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return proveedor

@proveedorRouter.post("/proveedor/create", tags=[tag])
async def create_proveedor(proveedor: Proveedores):
    # Insertar el proveedor en la base de datos MongoDB
    db.insert_one(proveedor.model_dump())

    # Eliminar la caché de proveedores en Redis para asegurar que los datos estén actualizados
    redis.json().delete("proveedores", "$")

    return {"mensaje": "Proveedor creado exitosamente."}


# Actualizar un proveedor
@proveedorRouter.put("/proveedor/update/{id}", tags=[tag])
async def updateProveedor(id: str, proveedor: Proveedores):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    # Convertir el modelo Pydantic a diccionario (excluyendo valores nulos)
    proveedor_dict = proveedor.dict(by_alias=True, exclude_none=True)

    # Actualizar el proveedor en MongoDB
    result = db.update_one({"_id": object_id}, {"$set": proveedor_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
    
    # Eliminar la caché de proveedores en Redis
    redis.json().delete(f"proveedor:{id}", "$")
    redis.json().delete("proveedores", "$")
    
    return {"mensaje": "Proveedor actualizado correctamente."}



# Eliminar un proveedor
@proveedorRouter.put("/proveedor/soft-delete/{id}", tags=[tag])
async def softProveedorDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor = db.find_one({"_id": object_id})
    
    if proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
    
    # Actualizar el estado del proveedor a "eliminado" (lógica de eliminación)
    db.update_one({"_id": object_id}, {"$set": {"estado": "eliminado"}})

    # Eliminar la caché de proveedores en Redis
    redis.json().delete(f"proveedor:{id}", "$")
    redis.json().delete("proveedores", "$")

    return {"mensaje": "Proveedor eliminado lógicamente."}


@proveedorRouter.delete("/proveedor/delete/all", tags=[tag])
async def deleteAllProveedores():
    # Eliminar todos los proveedores de la colección
    resultado = db.delete_many({})

    # Si no se eliminaron proveedores, lanzar una excepción
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay proveedores para eliminar.")
    
    # Eliminar la caché de proveedores en Redis
    redis.json().delete("proveedores", "$")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} proveedores."}
