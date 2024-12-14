def categoriaSerializer(categoria) -> dict:
    return {
        "_id": str(categoria["_id"]),
        "nombre": categoria["nombre"],
        "productos": categoria["productos"],
    }
    
def listCategoriaSerializer(categorias) -> list:
    return [categoriaSerializer(categoria) for categoria in categorias]