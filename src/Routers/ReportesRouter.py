from fastapi import APIRouter, HTTPException
from src.models.ReportesModels import Reporte
from src.Repository.mongodb import database
from bson import ObjectId

reporteRouter = APIRouter()

dbReportes = database["reportes"]
tag = "Reportes"

#Listar todos los reportes
@reporteRouter.get("/reporte/all", tags=[tag])
async def getAllReportes ():
    reportes = list(dbReportes.find())
    return reportes

#Traer un reporte por id
@reporteRouter.get("/reporte/{id}", tags=[tag])
async def getReportes(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    reporte = dbReportes.find_one({"_id": object_id})
    
    if reporte is not None:
        reporte["_id"] = str(reporte["_id"])
        return reporte

#Crear un reporte
@reporteRouter.post("/reporte/create", tags=[tag])
async def createReporte (reporte: Reporte):
    reporte = reporte.model_dump()
    dbReportes.insert_one(reporte)

#Actualizar un reporte
@reporteRouter.put("/reporte/update/{id}", tags=[tag])
async def update(id: str, reporte_update: Reporte):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    reporte_update = reporte_update.model_dump()

    dbReportes.update_one({"_id": object_id}, {"$set": reporte_update})
    
    return {"mensaje": "Reporte actualizado."}


#Borrar logicamente un reporte
@reporteRouter.put("/reporte/soft-delete/{id}", tags=[tag])
async def softDelete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")
    
    reporte = dbReportes.find_one({"_id": object_id})
    
    if reporte is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    
    dbReportes.update_one({"_id": object_id}, {"$set": {"estado": 0}})
    
    return {"mensaje": "Reporte eliminado."}