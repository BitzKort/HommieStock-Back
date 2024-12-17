def categoriaSerializer(categoria) -> dict:
    return {
        "_id": str(categoria["_id"]),
        "nombre": categoria["nombre"],
        "descripcion": categoria["descripcion"],
        "productos": categoria["productos"],
        "estado": categoria["estado"],
    }


def listCategoriaSerializer(categorias) -> list:
    return [categoriaSerializer(categoria) for categoria in categorias]
