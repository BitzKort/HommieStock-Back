from fastapi import APIRouter, HTTPException
from src.models.PedidosModels import Pedido
from src.schemas import PedidosSchemas
from src.Repository.mongodb import database
from bson import ObjectId
from src.Repository.redis import redis
import time

pedidoRouter = APIRouter()

dbPedidos = database["pedidos"]
dbInventario = database["inventarios"]
tag = "Pedidos"

# Listar todos los pedidos
@pedidoRouter.get("/pedido/all", tags=[tag])
async def getAllPedidos():
    start = time.time()
    
    pedidos = redis.json().get("pedidos", "$")  # Intenta obtener los pedidos de Redis

    if pedidos is None:
        pedidos = PedidosSchemas.listPedidoSerializer(dbPedidos.find())  # Si no están en Redis, los obtiene de MongoDB
        redis.json().set("pedidos", "$", pedidos)  # Guardar los pedidos en Redis
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")
        
    return pedidos

# Traer un pedido por ID
@pedidoRouter.get("/pedido/{id}", tags=[tag])
async def getPedido(id: str):
    start = time.time()
    
    # Verificar si el pedido está en Redis
    pedido_cache = redis.json().get(f"pedido:{id}", "$")

    if pedido_cache is None:
        try:
            object_id = ObjectId(id)
        except Exception:
            raise HTTPException(status_code=400, detail="ID inválido.")
        
        pedido = dbPedidos.find_one({"_id": object_id})

        if pedido is not None:
            pedido["_id"] = str(pedido["_id"])
            # Guardar el pedido individual en Redis para futuras consultas
            redis.json().set(f"pedido:{id}", "$", pedido)
        else:
            raise HTTPException(status_code=404, detail="Pedido no encontrado.")
        
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        pedido = pedido_cache
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return pedido

# Traer pedidos por cliente
@pedidoRouter.get("/pedido/cliente/{cliente_id}", tags=["Pedidos"])
async def getPedidos_por_cliente(cliente_id: str):
    start = time.time()

    # Intenta obtener los pedidos del cliente desde Redis
    pedidos_cache = redis.json().get(f"pedidos_cliente:{cliente_id}", "$")

    if pedidos_cache is None:
        pedidos = list(dbPedidos.find({"cliente.id": cliente_id}))
        for pedido in pedidos:
            pedido["_id"] = str(pedido["_id"])
        
        # Guardar los pedidos por cliente en Redis
        redis.json().set(f"pedidos_cliente:{cliente_id}", "$", pedidos)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        pedidos = pedidos_cache
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")

    return pedidos

#Crear un pedido
@pedidoRouter.post("/pedido/create", tags=["Pedidos"])
async def create_pedido(pedido: Pedido):
    # Validar stock
    for producto in pedido.productos:
        inventario = dbInventario.find_one({"productos.id": producto.id})
        if not inventario or inventario["stock"] < producto.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para el producto: {producto.nombre}"
            )
    
    # Reducir stock en inventario
    for producto in pedido.productos:
        dbInventario.update_one(
            {"productos.id": producto.id},
            {"$inc": {"stock": -producto.cantidad}}
        )
    
    # Guardar pedido en la base de datos MongoDB
    dbPedidos.insert_one(pedido.model_dump())

    # Eliminar la caché de pedidos en Redis para asegurar que los datos estén actualizados
    redis.json().delete("pedidos", "$")

    return {"mensaje": "Pedido creado exitosamente."}


#Actualizar un pedido
# Actualizar un pedido
@pedidoRouter.put("/pedido/update/{id}", tags=[tag])
async def update_pedido(id: str, pedido_update: Pedido):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Convertir cliente y productos a diccionario
    pedido_update.cliente = dict(pedido_update.cliente)
    pedido_update.productos = [dict(p) for p in pedido_update.productos]

    # Actualizar pedido en MongoDB
    result = dbPedidos.update_one({"_id": object_id}, {"$set": dict(pedido_update)})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    # Eliminar la caché del pedido individual y la lista completa
    redis.json().delete(f"pedido:{id}", "$")
    redis.json().delete("pedidos", "$")

    return {"mensaje": "Pedido actualizado correctamente."}


# Actualizar estado de un pedido
@pedidoRouter.put("/pedido/update/{id}/estado", tags=["Pedidos"])
async def update_estado_pedido(id: str, estado: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Actualizar el estado del pedido en MongoDB
    result = dbPedidos.update_one(
        {"_id": object_id}, {"$set": {"estado": estado}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    # Eliminar la caché del pedido individual y la lista completa
    redis.json().delete(f"pedido:{id}", "$")
    redis.json().delete("pedidos", "$")

    return {"mensaje": f"Estado del pedido actualizado a {estado}."}


# Borrar lógicamente un pedido
@pedidoRouter.put("/pedido/soft-delete/{id}", tags=["Pedidos"])
async def soft_delete_pedido(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Actualizar estado del pedido a "eliminado" en MongoDB
    result = dbPedidos.update_one({"_id": object_id}, {"$set": {"estado": "eliminado"}})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")

    # Eliminar la caché del pedido individual y la lista completa
    redis.json().delete(f"pedido:{id}", "$")
    redis.json().delete("pedidos", "$")

    return {"mensaje": "Pedido eliminado lógicamente."}

