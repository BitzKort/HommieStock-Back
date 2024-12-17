from fastapi import APIRouter, HTTPException
from src.models.ProductosModels import Producto, Contactos, Proveedores
from src.Repository.mongodb import database
from src.schemas.ProductoSchemas import listProductoSerializer
from bson import ObjectId
from src.Repository.redis import redis
import time

productoRouter = APIRouter()

db = database["productos"]
tag = "Productos"

# Listar todos los productos
@productoRouter.get("/producto/all", tags=[tag])
async def getAllProductos():
    start = time.time()

    # Intentar obtener los productos desde Redis
    productos = redis.json().get("productos", "$")

    if productos is None:
        # Si no están en Redis, obtenerlos desde MongoDB
        productos = listProductoSerializer(db.find())
        # Guardar los productos en Redis para futuras consultas
        redis.json().set("productos", "$", productos)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")
    
    return productos

# Traer un producto por ID
@productoRouter.get("/producto/{id}", tags=[tag])
async def getProducto(id: str):
    start = time.time()

    # Verificar si el producto está en Redis
    producto_cache = redis.json().get(f"producto:{id}", "$")

    if producto_cache is None:
        try:
            object_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID inválido.")
        
        # Obtener el producto desde MongoDB
        producto = db.find_one({"_id": object_id})

        if producto is not None:
            producto["_id"] = str(producto["_id"])
            # Guardar el producto individual en Redis para futuras consultas
            redis.json().set(f"producto:{id}", "$", producto)
        else:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        producto = producto_cache
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

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


@productoRouter.post("/producto/create", tags=[tag])
async def create(producto: Producto):
    # Convertir proveedores a diccionario
    print(producto.proveedores)
    producto.proveedores = toDict(producto.proveedores)

    # Insertar el producto en la base de datos
    db.insert_one(dict(producto))

    # Eliminar la caché de la lista de productos en Redis
    redis.json().delete("productos", "$")

    return {"mensaje": "Producto creado correctamente."}



@productoRouter.put("/producto/update/{id}", tags=[tag])
async def updateProducto(id: str, proveedor: Proveedores):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    proveedor.proveedores = toDict(proveedor.proveedores)
    db.update_one({"_id": object_id}, {"$set": dict(proveedor)})

    # Eliminar la caché del producto individual y la lista de productos
    redis.json().delete(f"producto:{id}", "$")
    redis.json().delete("productos", "$")
    
    return {"mensaje": "Proveedor actualizado correctamente."}


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
@productoRouter.delete("/producto/delete/all", tags=[tag])
async def delete_all_productos():
    # Eliminar todos los documentos de la colección
    resultado = db.delete_many({})

    # Si no se eliminó ningún producto, lanzar excepción
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay productos para eliminar.")

    # Eliminar la caché de la lista de productos en Redis
    redis.json().delete("productos", "$")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} productos."}
