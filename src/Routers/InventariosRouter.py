from fastapi import APIRouter, HTTPException
from src.models.InventariosModels import Inventario
from src.Repository.mongodb import database
from src.schemas.InventariosSchemas import listInventarioSerializer
from bson import ObjectId

inventarioRouter = APIRouter()

dbInventarios = database["inventarios"]
dbTiendas = database["tiendas"]

tag = "Inventarios"

#Listar todos los inventarios
@inventarioRouter.get("/inventario/all", tags=[tag])
async def getAllInventarios():
    inventarios = listInventarioSerializer(dbInventarios.find())
    return inventarios

#Traer un inventario por id
@inventarioRouter.get("/inventario/{id}", tags=[tag])
async def getInventarios(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    inventario = dbInventarios.find_one({"_id": object_id})
    
    if inventario is not None:
        inventario["_id"] = str(inventario["_id"])
        return inventario
    
#Listar inventarios por id de las tiendas
@inventarioRouter.get("/inventario/tienda/{id}", tags=[tag])
async def getInventarioByTienda (id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    inventarios = dbInventarios.find({"ubicacionTienda": id})
    
    inventarios = [Inventario(**documento) for documento in inventarios]

    return inventarios 

#Crear un inventario
@inventarioRouter.post("/inventario/create", tags=[tag])
async def createInventario (inventario: Inventario):
    
    inventario = inventario.model_dump()
    IdTienda = inventario.pop("ubicacionTienda")
    
    resultado = dbInventarios.insert_one(inventario)
    IdInventario = resultado.inserted_id
    
    dbTiendas.update_one(
        {"_id": ObjectId(IdTienda)},
        {"$push": {"inventarios": str(IdInventario)}}
        )
    
    return {"mensaje": "Inventario creado exitosamente", "inventario_id": str(IdInventario)}

#Actualizar un inventario
@inventarioRouter.put("/inventario/update/{id}", tags=[tag])
async def update(id: str, inventario_update: Inventario):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    inventario_update = inventario_update.model_dump()

    dbInventarios.update_one({"_id": object_id}, {"$set": inventario_update})
    
    return {"mensaje": "Inventario actualizado."}


#Borrar logicamente un inventario
@inventarioRouter.put("/inventario/soft-delete/{id}", tags=[tag])
async def softDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    inventario = dbInventarios.find_one({"_id": object_id})
    
    if inventario is None:
        raise HTTPException(status_code=404, detail="Inventario no encontrado.")
    
    dbInventarios.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Inventario eliminado."}
