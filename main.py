from fastapi import FastAPI, APIRouter
from src.Routers.ProductosRouter import productoRouter
from src.Routers.TiendasRouter import tiendaRouter
from src.Routers.CategoriasRouter import categoriaRouter
from src.Routers.ClientesRouter import clienteRouter
from src.Routers.DevolucionesRouter import devolucionRouter
from src.Routers.PedidosRouter import pedidoRouter
from src.Routers.ProveedoresRouter import proveedorRouter
from src.Routers.InventariosRouter import inventarioRouter
from src.Routers.ReportesRouter import reporteRouter
from src.Routers.ComprasRouter import compraRouter
from src.Repository.mongodb import database, connection, collections
app = FastAPI()
app.include_router(productoRouter)
app.include_router(tiendaRouter)
app.include_router(categoriaRouter)
app.include_router(clienteRouter)
app.include_router(devolucionRouter)
app.include_router(pedidoRouter)
app.include_router(proveedorRouter)
app.include_router(inventarioRouter)
app.include_router(reporteRouter)
app.include_router(compraRouter)


@app.get('/')
def status():
    try:
        dbName = database.name
        connection.admin.command('ping')
        return {"server": "up", 
                "mongoCluesterConnection":"Successfully", 
                "mongoDatabase": "{}".format(dbName),
                "collectionList": "{}".format(collections)}
    except Exception as e:
        print("error in mongo connection: {}".format(e))


if __name__ == '__main__':

    import uvicorn
    uvicorn.run(app,host = 'localhost', port= 8000)