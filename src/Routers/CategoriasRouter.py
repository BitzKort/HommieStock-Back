from fastapi import APIRouter, HTTPException
from src.models.CategoriasModels import Categoria
from src.Repository.mongodb import database
from src.schemas.CategoriaSchemas import listCategoriaSerializer
from bson import ObjectId
categoriaRouter = APIRouter()

db = database["categorias"]

#Traer toda la lista de categorias
@categoriaRouter.get("/categoria/all", tags=["Categorias"])
async def all():
    
    categorias = listCategoriaSerializer(db.find())
    return categorias

#Buscar categoría por ID
@categoriaRouter.get("/categoria/{id}", tags=["Categorias"])
async def get_categoria(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    categoria = db.find_one({"_id": object_id})
    
    if categoria is not None:
        categoria["_id"] = str(categoria["_id"])
        return categoria

#Crear una categoria
@categoriaRouter.post("/categoria/create", tags=["Categorias"])
async def create(categoria: Categoria):    
    categoria.productos = [dict(p) for p in categoria.productos]
    db.insert_one(dict(categoria)) 
    
#Actualizar una categoria
@categoriaRouter.put("/categoria/update/{id}", tags=["Categorias"])
async def update(id: str, categoria: Categoria):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    categoria.productos = [dict(p) for p in categoria.productos]
    db.update_one({"_id": object_id}, {"$set": dict(categoria)})
    
    return {"mensaje": "Categoría actualizada."}

#Borrado lógico de una categoría
@categoriaRouter.put("/categoria/soft-delete/{id}", tags=["Categorias"])
async def soft_delete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    categoria = db.find_one({"_id": object_id})
    
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Categoría eliminada."}

#Borrar todas las categorías (para pruebas)
@categoriaRouter.delete("/categoria/delete", tags=["Categorias"])
async def delete_all_categorias():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay categorías para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} categorías."}