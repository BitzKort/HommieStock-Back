from fastapi import APIRouter, HTTPException
from src.models.ProveedoresModels import Proveedores, Contacto, ProductoSuministrados
from src.Repository.mongodb import database
from src.schemas.ProveedoreSchemas import listproveedoreSerializer
from bson import ObjectId

proveedorRouter = APIRouter()

db = database["proveedores"]
tag = "Proveedores"

# Traer todos los proveedores
@proveedorRouter.get("/proveedor/all", tags=[tag])
async def getAllProveedor():
    proveedor = listproveedoreSerializer(db.find())
    return proveedor

# Crear un proveedor
@proveedorRouter.post("/proveedor/create", tags=[tag])
async def create(proveedor: Proveedores):
    db.insert_one(proveedor.model_dump())
    return {"mensaje": "Proveedor creado exitosamente."}

# Traer un proveedor por ID
@proveedorRouter.get("/proveedor/{id}", tags=[tag])
async def getProveedor(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    proveedor = db.find_one({"_id": object_id})
    
    if proveedor is not None:
        proveedor["_id"] = str(proveedor["_id"])
        return proveedor

# Actualizar un proveedor
@proveedorRouter.put("/proveedor/update/{id}", tags=[tag])
async def updateProveedor(id: str, proveedor: Proveedores):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor.contacto = dict(proveedor.contacto)
    proveedor.productosSuministrados = [dict(p) for p in proveedor.productosSuministrados]
    db.update_one({"_id": object_id}, {"$set": dict(proveedor)})
    
    return {"mensaje": "proveedor actualizado."}

# Eliminar un proveedor
@proveedorRouter.put("/proveedor/soft-delete/{id}", tags=[tag])
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

# Eliminar todos los proveedores
@proveedorRouter.delete("/proveedor/delete/all", tags=[tag])
async def deleteAllProvedoores():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay proveedores para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} proveedores."}