from fastapi import APIRouter
from src.models.Categoriasmodels import Categoria
from src.Repository.mongodb import database
from src.schemas.Categoriaschemas import listCategoriaSerializer
categoriaRouter = APIRouter()

db = database["categorias"]

@categoriaRouter.get("/categoria/all")
async def all():
    
    categorias = listCategoriaSerializer(db.find())
    return categorias

@categoriaRouter.post("/categoria/create")
async def create(categoria: Categoria):    
    categoria.productos = [dict(p) for p in categoria.productos]
    db.insert_one(dict(categoria))