def devolucionSerializer(devolucion) -> dict:
    return {
        "_id": str(devolucion["_id"]),
        "pedidoRe": devolucion["pedidoRe"],
        "motivoDevolucion": devolucion["motivoDevolucion"],
        "cantidadDevuelta": devolucion["cantidadDevuelta"],
        "fechaDevolucion": devolucion["fechaDevolucion"],
        "modoRetorno": devolucion["modoRetorno"],
        "estado": devolucion["estado"]
    }
    
def listDevolucionSerializer(devoluciones) -> list:
    return [devolucionSerializer(devolucion) for devolucion in devoluciones]