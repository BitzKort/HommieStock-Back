def inventarioSerializer(inventario) -> dict:
    return {
        "id": str(inventario["_id"]),
        "producto": inventario["productos"]
    }

def listPedidoSerializer(inventarios) -> list:
    return [inventarioSerializer(inventario) for inventario in inventarios]