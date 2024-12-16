import time
from fastapi import APIRouter, HTTPException
from src.models.ProductosModels import Producto, Contactos, Proveedores
from src.Repository.mongodb import database
from src.schemas.ProductoSchemas import listProductoSerializer
from bson import ObjectId
from src.Repository.redis import redis

productoRouter = APIRouter()

db = database["productos"]

# Traer toda la lista de productos
@productoRouter.get("/producto/all")
async def getAllProductos():
    start = time.time()

    # Intentamos obtener los productos desde Redis
    productos = redis.json().get("productos", "$")

    if productos is None:
        # Si no están en Redis, los obtenemos desde MongoDB
        productos = listProductoSerializer(db.find())
        # Guardamos los productos en Redis para futuras consultas
        redis.json().set("productos", "$", productos)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return productos


# Buscar producto por ID
@productoRouter.get("/producto/{id}")
async def getProducto(id: str):
    try:
        # Intentamos convertir el id a un ObjectId válido
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Primero intentamos buscar el producto en Redis
    producto = redis.json().get(f"producto:{id}", "$")

    if producto is None:
        # Si no está en Redis, buscamos en la base de datos
        producto = db.find_one({"_id": object_id})

        if producto is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        
        # Convertimos el _id de ObjectId a string antes de devolverlo
        producto["_id"] = str(producto["_id"])

        # Guardamos el producto en Redis para futuras consultas
        redis.json().set(f"producto:{id}", "$", producto)
    
    return producto


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