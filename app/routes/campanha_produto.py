from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from sqlalchemy.testing.pickleable import User

from app.auth2.token import get_current_user
from pydantic import BaseModel

from app.models.campanha_produto import (
    criar_campanha_produto,
    atualizar_campanha_produto,
    deletar_campanha_produto,
    listar_todos_campanha_produto,
    listar_campanha_produto_por_campanha,
    listar_campanha_produto_por_produto
)

from app.db.db import get_db
from app.utils.recupera_empresa import recuperar_empresa
from app.utils.transformadores_json import campanha_produto_to_dict
import logging


class CampanhaProdutoCreate(BaseModel):
    campanha_id: int
    produto_id: int
    valor_promocional: float
    frequencia_exibicao: int


class CampanhaProdutoUpdate(BaseModel):
    campanha_id: Optional[int] = None
    produto_id: Optional[int] = None
    valor_promocional: Optional[float] = None
    frequencia_exibicao: Optional[int] = None


router = APIRouter()


@router.post("/campanha-produto/incluir-produto-campanha")
async def incluir_produto_campanha(novo_produto_campanha: CampanhaProdutoCreate, usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f'Erro ao recuperar cnpj da empresa do usuário {str(e)}')
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="Erro ao encontrar o cnpj da empresa correspondente.")

        async with get_db(cnpj_empresa_user) as db:
            try:
                campanha_produto = await criar_campanha_produto(
                    db=db,
                    campanha_id=novo_produto_campanha.campanha_id,
                    produto_id=novo_produto_campanha.produto_id,
                    valor_promocional=novo_produto_campanha.valor_promocional,
                    frequencia_exibicao=novo_produto_campanha.frequencia_exibicao
                )
                campanha_produto_dict = campanha_produto_to_dict(campanha_produto)
                return {"status": "success", "campanha_produto": campanha_produto_dict}
            except Exception as e:
                logging.error(f'Erro ao incluir o produto na campanha: {str(e)}')
                raise HTTPException(status_code=500, detail='Erro ao incluir o produto na campanha.')
    except Exception as e:
        logging.error(f'Erro ao processar a requisição: {str(e)}')
        return {"status": "error", "message": str(e)}


@router.delete("/campanha-produto/deletar-produto-campanha/{campanha_produto_id}")
async def deletar_produto_campanha(campanha_produto_id: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='CNPJ da empresa não encontrado.')

        async with get_db(cnpj_empresa_user) as db:
            sucesso = await deletar_campanha_produto(db=db, campanha_produto_id=campanha_produto_id)
            if not sucesso:
                raise HTTPException(status_code=404, detail='Produto da campanha não encontrado.')
            return {"status": "success", "message": "Produto da campanha deletado com sucesso."}
    except Exception as e:
        logging.error(f'Erro ao deletar produto da campanha: {str(e)}')
        raise HTTPException(status_code=500, detail='Erro ao deletar produto da campanha.')


@router.patch("/campanha-produto/atualizar-produto-campanha/{campanha_produto_id}")
async def editar_produto_campanha(campanha_produto_id: int, dados_produto_campanha: CampanhaProdutoUpdate, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='CNPJ da empresa não encontrada.')

        async with get_db(cnpj_empresa_user) as db:
            campanha_produto_atualizada = await atualizar_campanha_produto(
                db=db, campanha_produto_id=campanha_produto_id,
                campanha_id=dados_produto_campanha.campanha_id,
                produto_id=dados_produto_campanha.produto_id,
                valor_promocional=dados_produto_campanha.valor_promocional,
                frequencia_exibicao=dados_produto_campanha.frequencia_exibicao
            )

            if not campanha_produto_atualizada:
                raise HTTPException(status_code=404, detail='Produto da campanha não encontrado.')

            campanha_produto_dict = campanha_produto_to_dict(campanha_produto_atualizada)
            return {"status": "success", "campanha_produto": campanha_produto_dict}
    except HTTPException as e:
        logging.error(f'Erro ao atualizar produto da campanha: {str(e)}')
        raise HTTPException(status_code=500, detail='Erro ao atualizar produto da campanha.')


@router.get("/campanha_produto/visualizar_campanhas_produtos")
async def visualizar_campanhas_produtos(usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            campanhas_produtos = await listar_todos_campanha_produto(db=db)
            return {"status": "success", "campanhas_produtos": campanhas_produtos}
    except HTTPException as e:
        logging.error(f"Erro ao listar os produtos de todas as campanhas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar os produtos de todas as campanhas.")


@router.get("/campanha_produto/visualizar_produtos_campanha/{campanha_id}")
async def visualizar_produtos_campanha(campanha_id: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await  recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produtos_campanha = await listar_campanha_produto_por_campanha(db=db, campanha_id=campanha_id)
            return {"status": "success", "campanha_produtos": produtos_campanha}
    except Exception as e:
        logging.error(f"Erro ao listar os produtos da campanha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar os produtos da campanha.")


@router.get("/campanha_produto/visualizar_campanhas_produto/{produto_id}")
async def visualizar_campanhas_produto(produto_id: int, usuario: User = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            campanhas_produto = await listar_campanha_produto_por_produto(db=db, produto_id=produto_id)
            return {"status": "success", "campanhas_produtos": campanhas_produto}
    except Exception as e:
        logging.error(f"Erro listar campanhas do produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar campanhas do produto.")

