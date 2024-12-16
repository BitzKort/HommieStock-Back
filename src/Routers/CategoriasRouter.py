import time
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from src.models.CategoriasModels import Categoria
from src.Repository.mongodb import database
from src.schemas.CategoriaSchemas import listCategoriaSerializer
from src.Repository.redis import redis

categoriaRouter = APIRouter()

db = database["categorias"]

# Traer toda la lista de categorías
@categoriaRouter.get("/categoria/all")
async def all():
    start = time.time()

    categorias = redis.json().get("categorias", "$")

    if categorias is None:
        categorias = listCategoriaSerializer(db.find())
        # Guardar en Redis
        redis.json().set("categorias", "$", categorias)
        end = time.time()
        run_time = end - start
        print(f"Run time (Without Redis): {run_time}")
    else:
        end = time.time()
        run_time = end - start
        print(f"Run time (With Redis): {run_time}")
    return categorias


# Buscar categoría por ID
@categoriaRouter.get("/categoria/{id}")
async def get_categoria(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    # Primero intentamos buscar en Redis
    categoria = redis.json().get(f"categoria:{id}", "$")

    if categoria is None:
        # Si no está en Redis, buscamos en la base de datos
        categoria = db.find_one({"_id": object_id})

        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoría no encontrada.")
        
        # Convertir el _id de ObjectId a string para devolverlo de forma correcta
        categoria["_id"] = str(categoria["_id"])

        # Guardamos la categoría en Redis para futuras consultas
        redis.json().set(f"categoria:{id}", "$", categoria)
        
    return categoria

#Crear una categoria
@categoriaRouter.post("/categoria/create")
async def create(categoria: Categoria):    
    categoria.productos = [dict(p) for p in categoria.productos]
    db.insert_one(dict(categoria)) 
    
#Actualizar una categoria
@categoriaRouter.put("/categoria/update/{id}")
async def update(id: str, categoria: Categoria):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    categoria.productos = [dict(p) for p in categoria.productos]
    db.update_one({"_id": object_id}, {"$set": dict(categoria)})
    
    return {"mensaje": "Categoría actualizada."}

#Borrado lógico de una categoría
@categoriaRouter.put("/categoria/soft-delete/{id}")
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
@categoriaRouter.delete("/categoria/delete")
async def delete_all_categorias():
    resultado = db.delete_many({})
    
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay categorías para eliminar.")
    
    return {"mensaje": f"Se eliminaron {resultado.deleted_count} categorías."}