from fastapi import APIRouter, HTTPException
from src.models.ProveedoresModels import Proveedores, Contacto, ProductoSuministrados
from src.Repository.mongodb import database
from src.schemas.ProveedoreSchemas import listproveedoreSerializer
from bson import ObjectId

proveedorRouter = APIRouter()

db = database["proveedores"]


@proveedorRouter.get("/proveedor/all")
async def getAllProveedor():

    proveedor = listproveedoreSerializer(db.find())
    return proveedor


@proveedorRouter.post("/proveedor/create")

async def create(proveedor: Proveedores):

    proveedor.contacto = dict(proveedor.contacto)
    proveedor.productosSuministrados = [dict(p) for p in proveedor.productosSuministrados]
    db.insert_one(dict(proveedor))


@proveedorRouter.get("/proveedor/{id}")

async def getProveedor(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    proveedor = db.find_one({"_id": object_id})
    
    if proveedor is not None:
        proveedor["_id"] = str(proveedor["_id"])
        return proveedor


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