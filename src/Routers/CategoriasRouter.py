from fastapi import APIRouter, HTTPException
from src.models.CategoriasModels import Categoria
from src.Repository.mongodb import database
from src.schemas.CategoriaSchemas import listCategoriaSerializer
from bson import ObjectId
from src.Repository.redis import redis
import time

categoriaRouter = APIRouter()

db = database["categorias"]


# Traer toda la lista de categorias
@categoriaRouter.get("/categoria/all", tags=["Categorias"])
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
@categoriaRouter.get("/categoria/{id}", tags=["Categorias"])
async def get_categoria(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    categoria = redis.json().get(f"categoria:{id}", "$")

    if categoria is None:
        categoria = db.find_one({"_id": object_id})
        if categoria is None:
            raise HTTPException(status_code=404, detail="Categoría no encontrada.")

        categoria["_id"] = str(categoria["_id"])

        redis.json().set(f"categoria:{id}", "$", categoria)
    else:
        categoria = categoria[0]

    return categoria


# Crear una categoria
@categoriaRouter.post("/categoria/create", tags=["Categorias"])
async def create(categoria: Categoria):
    categoria.productos = [dict(p) for p in categoria.productos]
    db.insert_one(dict(categoria))
    redis.delete("categorias")


# Actualizar una categoria
@categoriaRouter.put("/categoria/update/{id}", tags=["Categorias"])
async def update(id: str, categoria: Categoria):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    categoria.productos = [dict(p) for p in categoria.productos]

    result = db.update_one({"_id": object_id}, {"$set": dict(categoria)})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    redis.delete(f"categoria:{id}")
    redis.delete("categorias")

    return {"mensaje": "Categoría actualizada."}


# Borrado lógico de una categoría
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

    redis.delete(f"categoria:{id}")
    redis.delete("categorias")

    return {"mensaje": "Categoría eliminada correctamente (soft delete)."}


# Borrar todas las categorías (para pruebas)
@categoriaRouter.delete("/categoria/delete", tags=["Categorias"])
async def delete_all_categorias():
    resultado = db.delete_many({})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No hay categorías para eliminar.")

    redis.delete("categorias")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} categorías."}
