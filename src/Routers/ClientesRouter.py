from fastapi import APIRouter, HTTPException
from src.models.ClientesModels import Cliente
from src.Repository.mongodb import database
from src.schemas.ClienteSchemas import listClienteSerializer
from bson import ObjectId
clienteRouter = APIRouter()

db = database["clientes"]

#Traer todos los clientes
@clienteRouter.get("/cliente/all", tags=["Clientes"])
async def all():
    clientes = listClienteSerializer(db.find())
    return clientes

#Buscar cliente por ID
@clienteRouter.get("/cliente/{id}", tags=["Clientes"])
async def get_cliente(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    cliente = db.find_one({"_id": object_id})
    
    if cliente is not None:
        cliente["_id"] = str(cliente["_id"])
        return cliente

#Crear un cliente
@clienteRouter.post("/cliente/create", tags=["Clientes"])
async def create(cliente: Cliente):    
    cliente.historialPedidos = [dict(p) for p in cliente.historialPedidos]
    db.insert_one(dict(cliente))
    
#Actualizar un cliente
@clienteRouter.put("/cliente/update/{id}", tags=["Clientes"])
async def update(id: str, cliente: Cliente):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    cliente.historialPedidos = [dict(p) for p in cliente.historialPedidos]
    db.update_one({"_id": object_id}, {"$set": dict(cliente)})
    
    return {"mensaje": "Cliente actualizado."}

#Borrado lógico de un cliente
@clienteRouter.put("/cliente/soft-delete/{id}", tags=["Clientes"])
async def soft_delete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    cliente = db.find_one({"_id": object_id})
    
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Cliente eliminado."}

#Borrar todas los clientes (para pruebas)
@clienteRouter.delete("/cliente/delete", tags=["Clientes"])
async def delete_all_clientes():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay clientes para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} clientes."}