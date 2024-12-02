from fastapi import APIRouter


prodRouter = APIRouter()


@prodRouter.get('/clientes/all')

async def get_all():
    return {"message":"does not implement yet"}