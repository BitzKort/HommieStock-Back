def tiendaSerializer(tienda) -> dict:
    return {
        "id": str(tienda["_id"]),
        "nombre": tienda["nombre"],
        "direccion": tienda["direccion"],
        "ciudad": tienda["ciudad"],
        "codPostal": tienda["codPostal"],
        "capacidadAlmacenamiento": tienda["capacidadAlmacenamiento"],
        "horarioOperacion": tienda["horarioOperacion"],
        "estado": tienda["estado"],
        "inventarios": tienda["inventarios"]

    }

def listTiendaSerializer(tiendas) -> list:
    return [tiendaSerializer(tienda) for tienda in tiendas]