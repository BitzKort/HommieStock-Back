from fastapi import APIRouter, HTTPException
from src.models.DevolucionesModels import Devolucion
from src.Repository.mongodb import database
from src.schemas.DevolucioneSchemas import listDevolucionSerializer
from bson import ObjectId
from src.Repository.redis import redis

devolucionRouter = APIRouter()

db = database["devoluciones"]
db_inventarios = database["inventarios"]
db_devoluciones = database["devoluciones"]


# Traer toda la lista de devoluciones
@devolucionRouter.get("/devolucion/all", tags=["Devoluciones"])
async def all():
    devoluciones = redis.json().get("devoluciones", "$")

    if devoluciones is None:
        devoluciones = listDevolucionSerializer(db.find())
        redis.json().set("devoluciones", "$", devoluciones)
    else:
        devoluciones = devoluciones[0]

    return devoluciones


# Buscar devolución por ID
@devolucionRouter.get("/devolucion/{id}", tags=["Devoluciones"])
async def get_devolucion(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    devolucion = redis.json().get(f"devolucion:{id}", "$")

    if devolucion is None:
        devolucion = db.find_one({"_id": object_id})
        if devolucion is None:
            raise HTTPException(status_code=404, detail="Devolución no encontrada.")

        devolucion["_id"] = str(devolucion["_id"])
        redis.json().set(f"devolucion:{id}", "$", devolucion)
    else:
        devolucion = devolucion[0]

    return devolucion


@devolucionRouter.post("/devolucion/create", tags=["Devoluciones"])
async def create_devolucion(devolucion: Devolucion):
    devolucion_dict = devolucion.model_dump()
    listPedidos = [dict(p) for p in devolucion.pedidoRe]

    for pedido_item in listPedidos:
        producto_id = pedido_item["producto"]
        cantidad_devuelta = pedido_item["cantidad"]

        inventario_item = db_inventarios.find_one({"productos.id": producto_id})
        if not inventario_item:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {producto_id} no encontrado en el inventario.",
            )

        nuevo_stock = inventario_item["stock"] + cantidad_devuelta
        db_inventarios.update_one(
            {"_id": inventario_item["_id"]},
            {
                "$set": {
                    "stock": nuevo_stock,
                    "fechaUltimaAct": devolucion.fechaDevolucion,
                }
            },
        )

    result = db_devoluciones.insert_one(devolucion_dict)
    redis.delete("inventarios")
    redis.delete("devoluciones")

    return {
        "message": "Devolución creada y stock actualizado",
        "devolucion_id": str(result.inserted_id),
    }


# Actualizar una devolución
@devolucionRouter.put("/devolucion/update/{id}", tags=["Devoluciones"])
async def update(id: str, devolucion: Devolucion):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    devolucion.pedidoRe = [dict(p) for p in devolucion.pedidoRe]
    result = db.update_one({"_id": object_id}, {"$set": dict(devolucion)})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Devolución no encontrada.")

    redis.delete(f"devolucion:{id}")
    redis.delete("devoluciones")

    return {"mensaje": "Devolución actualizada correctamente."}


# Borrado lógico de una devolución
@devolucionRouter.put("/devolucion/soft-delete/{id}", tags=["Devoluciones"])
async def soft_delete(id: str):
    try:
        object_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido.")

    devolucion = db.find_one({"_id": object_id})
    if devolucion is None:
        raise HTTPException(status_code=404, detail="Devolución no encontrada.")

    db.update_one({"_id": object_id}, {"$set": {"estado": 0}})

    redis.delete(f"devolucion:{id}")
    redis.delete("devoluciones")

    return {"mensaje": "Devolución eliminada correctamente (soft delete)."}


# Borrar todas las devoluciones (para pruebas)
@devolucionRouter.delete("/devolucion/delete", tags=["Devoluciones"])
async def delete_all_devoluciones():
    resultado = db.delete_many({})

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404, detail="No hay devoluciones para eliminar."
        )

    redis.delete("devoluciones")

    return {"mensaje": f"Se eliminaron {resultado.deleted_count} devoluciones."}
