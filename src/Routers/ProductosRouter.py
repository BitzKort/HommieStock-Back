from fastapi import APIRouter, HTTPException
from src.models.ProductosModels import Producto, Contactos, Proveedores
from src.Repository.mongodb import database
from src.schemas.ProductoSchemas import listProductoSerializer
from bson import ObjectId

productoRouter = APIRouter()

db = database["productos"]

@productoRouter.get("/producto/all")
async def getAllProductos():

    productos = listProductoSerializer(db.find())
    return productos


def toDict(obj):

    if isinstance(obj, Proveedores):
        print("es un provedor")
        return {
            "nombre": toDict(obj.nombre),
            "precioCompra": toDict(obj.precioCompra),
            "contacto": toDict(obj.contacto)
        }

    elif isinstance(obj, Contactos):
        print("Es un contacto")
        return {
            "telefono": obj.telefono,
            "email": obj.email
        }

    elif isinstance(obj, list):
        print("Es una lista")
        return [toDict(element) for element in obj]

    else:
        print("cae aqui devuele normal")
        return obj


@productoRouter.post("/producto/create")

async def create(producto: Producto):

    print(producto.proveedores)
    producto.proveedores = toDict(producto.proveedores)
    db.insert_one(dict(producto))

@productoRouter.get("/producto/{id}")

async def getProducto(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    producto = db.find_one({"_id": object_id})
    
    if producto is not None:
        producto["_id"] = str(producto["_id"])
        return producto

@productoRouter.put("/producto/update/{id}")

async def updateProducto(id: str, proveedor: Proveedores):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor.proveedores = toDict(proveedor.proveedores)
    db.update_one({"_id": object_id}, {"$set": dict(proveedor)})
    
    return {"mensaje": "Proveedor actualizado."}


'''
@productoRouter.put("/producto/soft-delete/{id}")

async def softProductoDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    producto = db.find_one({"_id": object_id})
    
    if producto is None:
        raise HTTPException(status_code=404, detail="producto no encontrado.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Producto eliminado."}
'''
@productoRouter.delete("/producto/delete/all")

async def delete_all_productors():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay productos para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} productos."}