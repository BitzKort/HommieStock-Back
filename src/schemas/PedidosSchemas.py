def pedidoSerializer(pedido) -> dict:
    return {
        "id": str(pedido["_id"]),
        "cliente": pedido["cliente"],
        "productos": pedido["productos"],
        "precioTotal": pedido["precioTotal"],
        "estado": pedido["estado"],
        "fechaPedido": pedido["fechaPedido"]
    }

def listPedidoSerializer(pedidos) -> list:
    return [pedidoSerializer(pedido) for pedido in pedidos]