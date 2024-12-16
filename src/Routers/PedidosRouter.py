from fastapi import APIRouter, HTTPException
from src.models.PedidosModels import Pedido
from src.schemas import PedidosSchemas
from src.Repository.mongodb import database
from bson import ObjectId

pedidoRouter = APIRouter()

dbPedidos = database["pedidos"]
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

#Crear un pedido
@pedidoRouter.post("/pedido/create", tags=[tag])
async def createPedido (pedido: Pedido):
    pedido.cliente = dict(pedido.cliente)
    pedido.productos = [dict(producto) for producto in pedido.productos]
    dbPedidos.insert_one(dict(pedido))

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


#Borrar logicamente un pedido
@pedidoRouter.put("/pedido/soft-delete/{id}", tags=[tag])
async def softDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    devolucion = dbPedidos.find_one({"_id": object_id})
    
    if devolucion is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrada.")
    
    dbPedidos.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Pedido eliminado."}
