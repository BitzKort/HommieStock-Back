def productoSerializer(producto) ->dict:
    return {
        "_id":str(producto["_id"]),
        "nombre": producto["nombre"],
        "descripcion": producto["descripcion"],
        "numeroSerie":producto["numeroSerie"],
        "categoria": producto["categoria"],
        "precioUnitario": producto["precioUnitario"],
        "fechaCaducidad":producto["fechaCaducidad"],
        "proveedores": producto["proveedores"]
    }

def listProductoSerializer(productos) -> list:
    return [productoSerializer(producto) for producto in productos]