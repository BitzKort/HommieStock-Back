def clienteSerializer(cliente) -> dict:
    return {
        "_id": str(cliente["_id"]),
        "nombre": cliente["nombre"],
        "direccion": cliente["direccion"],
        "ciudad": cliente["ciudad"],
        "codPostal": cliente["codPostal"],
        "historialPedidos": cliente["historialPedidos"],
    }
    
def listClienteSerializer(clientes) -> list:
    return [clienteSerializer(cliente) for cliente in clientes]