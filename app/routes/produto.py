from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.auth2.token import get_current_user
from app.models.produto import (
    criar_produto,
    buscar_produto,
    listar_produtos,
    deletar_produto,
    atualizar_produto
)
from app.db.db import get_db
from app.utils.recupera_empresa import recuperar_empresa
from app.utils.transformadores_json import produto_to_dict
import logging


class ProdutoCreate(BaseModel):
    nome: str
    descricao: str
    codigo_produto: str
    unidade_medida: str
    preco_venda: float
    qtd_estoque: int
    link: str


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    codigo_produto: Optional[str] = None
    unidade_medida: Optional[str] = None
    preco_venda: Optional[float] = None
    qtd_estoque: Optional[int] = None
    link: Optional[str] = None


router = APIRouter()


# Cadastrar Produto
@router.post("/produto/cadastrar-produto")
async def cadastrar_produto(novo_produto: ProdutoCreate, usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f'Erro ao recuperar cnpj da empresa do usuário: {str(e)}')
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao encontrar o cnpj da empresa correspondente.')

        async with get_db(cnpj_empresa_user) as db:
            try:
                produto = await criar_produto(
                    db=db,
                    nome=novo_produto.nome,
                    descricao=novo_produto.descricao,
                    codigo_produto=novo_produto.codigo_produto,
                    unidade_medida=novo_produto.unidade_medida,
                    preco_venda=novo_produto.preco_venda,
                    qtd_estoque=novo_produto.qtd_estoque,
                    link=novo_produto.link
                )
                produto_dict = produto_to_dict(produto)
                return {"status": "success", "produto": produto_dict}
            except Exception as e:
                logging.error(f'Erro ao cadastrar produto: {str(e)}')
                raise HTTPException(status_code=500, detail='Erro ao cadastrar produto.')
    except HTTPException as e:
        logging.info(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e.detail)}


# Deletar Produto
@router.delete("/produto/deletar-produto/{id_produto}")
async def deletar_produto_endpoint(id_produto: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            sucesso = await deletar_produto(db=db, produto_id=id_produto)
            if not sucesso:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")
            return {"status": "success", "message": "Produto deletado com sucesso."}
    except Exception as e:
        logging.error(f"Erro ao deletar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao deletar produto.")


# Atualizar Produto
@router.patch("/produto/atualizar-produto/{id_produto}")
async def atualizar_produto_endpoint(id_produto: int, dados_produto: ProdutoUpdate, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produto_atualizado = await atualizar_produto(db=db, produto_id=id_produto, nome=dados_produto.nome, descricao=dados_produto.descricao,
                                                         codigo_produto=dados_produto.codigo_produto, unidade_medida=dados_produto.unidade_medida,
                                                         preco_venda=dados_produto.preco_venda, qtd_estoque=dados_produto.qtd_estoque,
                                                         link=dados_produto.link)
            if not produto_atualizado:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")

            produto_dict = produto_to_dict(produto_atualizado)
            return {"status": "success", "produto": produto_dict}
    except Exception as e:
        logging.error(f"Erro ao atualizar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto.")


# Buscar Produto por ID
@router.get("/produto/buscar-produto/{id_produto}")
async def buscar_produto_endpoint(id_produto: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produto = await buscar_produto(db=db, produto_id=id_produto)
            if not produto:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")
            produto_dict = produto_to_dict(produto)
            return {"status": "success", "produto": produto_dict}
    except Exception as e:
        logging.error(f"Erro ao buscar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produto.")


# Listar Todos os Produtos
@router.get("/produto/listar-produtos")
async def listar_produtos_endpoint(usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produtos = await listar_produtos(db=db)
            return {"status": "success", "produtos": produtos}
    except Exception as e:
        logging.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar produtos.")
