from fastapi import APIRouter, HTTPException
from src.models.ReportesModels import Reporte, ReporteStockTienda
from src.Repository.mongodb import database
from bson import ObjectId

from src.schemas.ReportesSchemas import listReporteSerializer

reporteRouter = APIRouter()

dbReportes = database["reportes"]
tag = "Reportes-CRUD"
tag2 = "Reportes - Proyecto"
db_tiendas = database["tiendas"]
db_inventarios = database["inventarios"]


#Listar todos los reportes
@reporteRouter.get("/reporte/all", tags=[tag])
async def getAllReportes ():
    reportes = listReporteSerializer(dbReportes.find())
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


#Esto es para crear un reporte pero como utilizamos especificamente los pedidos por el profe no es necesario al menos
#que quieran utilizarlo ahi esta.

#Crear un reporte
#@reporteRouter.post("/reporte/create", tags=[tag])
#async def createReporte (reporte: Reporte):
    #reporte = reporte.model_dump()
    #dbReportes.insert_one(reporte)

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

@reporteRouter.post("/reporte-proyecto/create", tags=["Reportes"])
async def reporte_project_create(idTienda: str):
    
    try:
        object_id = ObjectId(idTienda)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tienda con ID {idTienda} no encontrada")
    
    tienda = db_tiendas.find_one({"_id": object_id})
    # Lista para almacenar inventarios detallados
    inventarios_tienda = []
    stock_total = 0

    # Buscar los inventarios asociados a la tienda
    print(tienda)
    for inventario_id in tienda["inventarios"]:
        print(inventario_id)
        try:
        
            inventario = ObjectId(inventario_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Inventario con ID {idTienda} no encontrado")
        
        
        inventario = db_inventarios.find_one({"_id": inventario})

        if inventario:
            print("llega aqui otra vez asalvo de casallas")
            producto_info = {
                "idProducto": inventario["productos"]["id"],
                "numeroSerie": inventario["productos"]["numeroSerie"],
                "nombreProducto": inventario["productos"]["nombre"],
                "categoria": inventario["productos"]["categoria"],
                "stock": inventario["stock"]
            }
            print("llega aqui por lo que veo")
            stock_total += inventario["stock"]

            print("y hasta aqui?")
            inventarios_tienda.append({
                "idInventario": str(inventario["_id"]),
                "producto": producto_info
            })

            print("paso esta parte")

    # Crear el reporte en el formato requerido
    reporte = {
        "datos": {

            "idTienda": idTienda,
            "TiendaNombre": tienda["nombre"],
            "inventariosTienda": inventarios_tienda,
            "stockTotal": stock_total
        }

    }

    # Guardar el reporte en la base de datos
    dbReportes.insert_one(dict(reporte))

    return reporte


@reporteRouter.post("/reporte-proyecto/costo-inventario", tags=["Reportes"])

async def reporteCostoInventario():

    pass