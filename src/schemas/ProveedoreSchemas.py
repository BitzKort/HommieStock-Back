
def proveedoreSerializer (proveedor) -> dict:

    return {

        "_id":str(proveedor["_id"]),
        "nombre": proveedor["nombre"],
        "direccion": proveedor["direccion"],
        "ciudad": proveedor["ciudad"],
        "codigoPostal": proveedor["codigoPostal"],
        "contacto": proveedor["contacto"],
        "productosSuministrados": proveedor["productosSuministrados"],
        "estado":proveedor["estado"]
    }

def listproveedoreSerializer(proveedores) -> list:
    
    return [proveedoreSerializer(proveedor) for proveedor in proveedores]