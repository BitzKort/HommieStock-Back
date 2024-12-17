from fastapi import APIRouter, HTTPException
from src.models.ReportesModels import Reporte
from src.Repository.mongodb import database
from bson import ObjectId

from src.schemas.ReportesSchemas import listReporteSerializer

reporteRouter = APIRouter()

dbReportes = database["reportes"]
tag = "Reportes-CRUD"
tag2 = "Reportes - Proyecto"
db_tiendas = database["tiendas"]
db_inventarios = database["inventarios"]
db_productos = database["productos"]
db_proveedores = database["proveedores"]


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

@reporteRouter.post("/reporte-proyecto/inventario-tienda", tags=["Reportes"])
async def reporte_inventario_tienda(idTienda: str):
    
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
       
        try:
        
            inventario = ObjectId(inventario_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Inventario con ID {idTienda} no encontrado")
        
        
        inventario = db_inventarios.find_one({"_id": inventario})

        if inventario:
           
            producto_info = {
                "idProducto": inventario["productos"]["id"],
                "numeroSerie": inventario["productos"]["numeroSerie"],
                "nombreProducto": inventario["productos"]["nombre"],
                "categoria": inventario["productos"]["categoria"],
                "stock": inventario["stock"]
            }
           
            stock_total += inventario["stock"]

            inventarios_tienda.append({
                "idInventario": str(inventario["_id"]),
                "producto": producto_info
            })


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

async def reporte_costo_inventario(idInventario: str):

    try:
        object_id = ObjectId(idInventario)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Inventario con ID {idInventario} no encontrado")
    
    inventario = db_inventarios.find_one({"_id": object_id})

    
    stockInventario = inventario["stock"]


    ReportenombreProducto = inventario["productos"]["nombre"]
    ReporteIdProducto = inventario["productos"]["id"]


    try:
        object_idProducto = ObjectId(ReporteIdProducto)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Producto con ID {object_idProducto} no encontrado")
    
    producto =db_productos.find_one({"_id": object_idProducto})




    ReporteIdProveedor  = producto["proveedores"][0]["id"]
    ReporteNombreProveedor  = producto["proveedores"][0]["nombre"]
    ReporteCostoProveedor = producto["proveedores"][0]["precioCompra"]

    ReporteCostoTotal = ReporteCostoProveedor*stockInventario


    ReporteCostoInventario = {
        "datos": {
            "idInventario": idInventario,
            "stock": stockInventario,
            "idProducto": ReporteIdProducto,
            "productoNombre": ReportenombreProducto,
            "idProveedor":ReporteIdProveedor,
            "proveedorNombre":ReporteNombreProveedor,
            "costoCompra": ReporteCostoProveedor,
            "costoTotal": ReporteCostoTotal
        }

    }

    dbReportes.insert_one(dict(ReporteCostoInventario))

    return ReporteCostoInventario

@reporteRouter.post("/reporte-proyecto/proveedor-productos", tags=["Reportes"])

async def reporte_proveedor_productos(idProveedor:str):

    try:
        objectIdProveedor = ObjectId(idProveedor)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Proveedor con ID {objectIdProveedor} no encontrado")
    
    proveedor =db_proveedores.find_one({"_id": objectIdProveedor})

    listProveedores = proveedor["productosSuministrados"]

    listReporteProductos =[]


    for producto in listProveedores:

        reportePRoducto = {

                "idProducto": producto["id"],
                "nombreProducto": producto["nombre"],
                "costoCompra": producto["precioCompra"]

        }
        listReporteProductos.append(reportePRoducto)
    
    ReportePRoveedorProductos = {
        "datos": {
            "idProveedor": idProveedor,
            "nombreProveedor": proveedor["nombre"],
            "listaProductos": listReporteProductos
        }
    }
    
    dbReportes.insert_one(dict(ReportePRoveedorProductos))

    return ReportePRoveedorProductos



@reporteRouter.post("/reporte-proyecto/productos-diferentes-tiendas", tags=["Reportes"])

async def Reporte_productos_diferentes_tiendas(idProducto: str):
        
        # Paso 1: Buscar los inventarios que contienen el producto específico
        inventarios_cursor = db_inventarios.find({"productos.id": idProducto})
        inventarios = [inventario for inventario in inventarios_cursor]
        
        if not inventarios:
            return {"mensaje": "No se encontraron inventarios con el producto especificado", "idProducto": idProducto}
        
        # Paso 2: Crear un diccionario para mapear las tiendas con los detalles del producto
        reporte = []

        
        for inventario in inventarios:
 
            tienda_id = inventario["ubicacionTienda"]
            stock = inventario["stock"]
            fechaUltimaAct = inventario["fechaUltimaAct"]

            try:

                objectIdTienda = ObjectId(tienda_id)
            
            except Exception:
                
                raise HTTPException(status_code=404, detail=f"Tienda con ID {objectIdTienda} no encontrada")            
            # Obtener detalles de la tienda
            tienda =  db_tiendas.find_one({"_id": objectIdTienda})

                        
            if tienda:


                # Crear una entrada con los datos relevantes
                reporteTienda = {
                    "tienda": {
                        "id": tienda_id,
                        "nombre": tienda["nombre"],
                    },
                    "producto": {
                        "id": idProducto,
                        "nombre": inventario["productos"]["nombre"],
                        "stock": stock,
                        "fechaUltimaActualizacion": fechaUltimaAct
                    }
                }

                reporte.append(reporteTienda)
        
        reporteProductoTiendas = {

            "datos": reporte
        }

        dbReportes.insert_one(dict(reporteProductoTiendas))


        return reporteProductoTiendas






