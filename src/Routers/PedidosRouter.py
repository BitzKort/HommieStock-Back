from fastapi import APIRouter, HTTPException
from src.models.PedidosModels import Pedido
from src.schemas import PedidosSchemas
from src.Repository.mongodb import database
from bson import ObjectId

pedidoRouter = APIRouter()

dbPedidos = database["pedidos"]
dbInventario = database["inventarios"]
tag = "Pedidos"

#Listar todos los pedidos
@pedidoRouter.get("/pedido/all", tags=[tag])
async def getAllPedidos ():
    pedidos = PedidosSchemas.listPedidoSerializer(dbPedidos.find())
    return pedidos

#Traer un pedido por id
@pedidoRouter.get("/pedido/{id}", tags=[tag])
async def getPedido(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    pedido = dbPedidos.find_one({"_id": object_id})
    
    if pedido is not None:
        pedido["_id"] = str(pedido["_id"])
        return pedido

#Traer pedidos por cliente
@pedidoRouter.get("/pedido/cliente/{cliente_id}", tags=["Pedidos"])
async def get_pedidos_por_cliente(cliente_id: str):
    pedidos = list(dbPedidos.find({"cliente.id": cliente_id}))
    for pedido in pedidos:
        pedido["_id"] = str(pedido["_id"])
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
    
    # Guardar pedido
    dbPedidos.insert_one(pedido.model_dump())
    return {"mensaje": "Pedido creado exitosamente."}

#Actualizar un pedido
@pedidoRouter.put("/pedido/update/{id}", tags=[tag])
async def update(id: str, pedido_update: Pedido):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    pedido_update.cliente = dict(pedido_update.cliente)
    pedido_update.productos = [dict(p) for p in pedido_update.productos]
    dbPedidos.update_one({"_id": object_id}, {"$set": dict(pedido_update)})
    
    return {"mensaje": "Pedido actualizada."}

#Actualizar estado de un pedido
@pedidoRouter.put("/pedido/update/{id}/estado", tags=["Pedidos"])
async def update_estado_pedido(id: str, estado: str):
    result = dbPedidos.update_one(
        {"_id": ObjectId(id)}, {"$set": {"estado": estado}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return {"mensaje": f"Estado del pedido actualizado a {estado}."}

#Borrar logicamente un pedido
@pedidoRouter.put("/pedido/soft-delete/{id}", tags=["Pedidos"])
async def soft_delete_pedido(id: str):
    result = dbPedidos.update_one({"_id": ObjectId(id)}, {"$set": {"estado": "eliminado"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado.")
    return {"mensaje": "Pedido eliminado."}

