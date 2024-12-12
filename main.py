from fastapi import FastAPI, APIRouter
from src.Routers.ProductosRouter import prodRouter
from src.Routers.TIendasRouter import tiendaRouter
from src.Repository.mongodb import database, connection, collections
app = FastAPI()
app.include_router(prodRouter)
app.include_router(tiendaRouter)


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