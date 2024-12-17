from fastapi import APIRouter, HTTPException
from src.models.ComprasModels import Compra
from src.Repository.mongodb import database
from bson import ObjectId
from datetime import datetime

compraRouter = APIRouter()

dbCompras = database["compras"]
dbInventarios = database["inventarios"]
dbProveedores = database["proveedores"]

tag = "Compras"

@compraRouter.post("/compra/create", tags=[tag])
async def create_compra(compra: Compra):
    # Validar proveedor
    proveedor = dbProveedores.find_one({"_id": ObjectId(compra.proveedor_id)})
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")

    # Actualizar inventario
    for producto_compra in compra.productos:
        inventario = dbInventarios.find_one({"productos.id": producto_compra.id_producto})
        if not inventario:
            raise HTTPException(
                status_code=404,
                detail=f"Inventario no encontrado para el producto: {producto_compra.id_producto}"
            )

        # Actualizar stock y última actualización
        dbInventarios.update_one(
            {"productos.id": producto_compra.id_producto},
            {
                "$inc": {"stock": producto_compra.cantidad},
                "$set": {"fechaUltimaAct": datetime.now().isoformat()},
            }
        )

    # Calcular total
    compra.total = sum(p.cantidad * p.precio_unitario for p in compra.productos)

    # Guardar compra
    dbCompras.insert_one(compra.model_dump())

    return {"mensaje": "Compra registrada exitosamente."}


@compraRouter.get("/compra/all", tags=[tag])
async def get_all_compras():
    compras = list(dbCompras.find())
    for compra in compras:
        compra["_id"] = str(compra["_id"])
    return compras