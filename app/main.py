from fastapi import FastAPI
from app.routes import (
    auth, usuario, empresa,
    contrato, produto, campanha,
    campanha_produto, join_wpp
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(empresa.router)
app.include_router(contrato.router)
app.include_router(produto.router)
app.include_router(campanha.router)
app.include_router(campanha_produto.router)
app.include_router(join_wpp.router)