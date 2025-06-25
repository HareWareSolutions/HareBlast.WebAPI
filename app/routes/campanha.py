from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.auth2.token import get_current_user
from pydantic import BaseModel
from app.models.campanha import (
    criar_campanha,
    atualizar_campanha,
    deletar_campanha,
    listar_campanhas,
    buscar_campanha_por_id
)

from app.db.db import get_db
from app.utils.recupera_empresa import recuperar_empresa
from app.utils.transformadores_json import campanha_to_dict
from datetime import date
import logging


class CampanhaCreate(BaseModel):
    nome: str
    inicio_campanha: date
    fim_campanha: date


class CampanhaUpdate(BaseModel):
    nome: Optional[str] = None
    inicio_campanha: Optional[date] = None
    fim_campanha: Optional[date] = None


router = APIRouter()


@router.post("/campanha/cadastrar-campanha")
async def cadastrar_campanha(nova_campanha: CampanhaCreate, usuario_atual: dict = Depends(get_current_user)):
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
                campanha = await criar_campanha(
                    db=db,
                    nome=nova_campanha.nome,
                    inicio_campanha=nova_campanha.inicio_campanha,
                    fim_campanha=nova_campanha.fim_campanha
                )
                campanha_dict = campanha_to_dict(campanha)
                return {"status": "success", "campanha": campanha_dict}
            except Exception as e:
                logging.error(f'Erro ao cadastrar campanha: {str(e)}')
                raise HTTPException(status_code=500, detail='Erro ao cadastrar campanha.')
    except HTTPException as e:
        logging.error(f'Erro ao processar a requisição: {str(e)}')
        return {"status": "error", "message": str(e)}


@router.delete("/campanha/deletar-campanha/{campanha_id}")
async def excluir_campanha(campanha_id: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            sucesso = await deletar_campanha(db=db, campanha_id=campanha_id)
            if not sucesso:
                raise HTTPException(status_code=404, detail="Campanha não encontrada.")
            return {"status": "success", "message": "Campanha deletada com sucesso."}
    except HTTPException as e:
        logging.error(f'Erro ao deletar campanha: {str(e)}')
        raise HTTPException(status_code=500, detail="Erro ao deletar campanha.")


@router.patch("/campanha/atualizar-campanha/{id_campanha}")
async def editar_campanha(id_campanha: int, dados_campanha: CampanhaUpdate, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            campanha_atualizada = await atualizar_campanha(db=db, campanha_id=id_campanha, nome=dados_campanha.nome,
                                                           inicio_campanha=dados_campanha.inicio_campanha, fim_campanha=dados_campanha.fim_campanha)

            if not campanha_atualizada:
                raise HTTPException(status_code=404, detail="Campanha não encontrada.")

            campanha_dict = campanha_to_dict(campanha_atualizada)
            return {"status": "success", "campanha": campanha_dict}
    except HTTPException as e:
        logging.error(f'Erro ao atualizar campanha: {str(e)}')
        raise HTTPException(status_code=500, detail="Erro ao atualizar campanha.")


@router.get("/campanha/pesquisar-campanha/{id-campanha}")
async def pesquisar_campanha(id_campanha: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            campanha = await buscar_campanha_por_id(db=db, campanha_id=id_campanha)

            if not campanha:
                raise HTTPException(status_code=404, detail="Campanha não encontrada.")
            campanha_dict = campanha_to_dict(campanha)
            return {"status": "success", "campanha": campanha_dict}
    except HTTPException as e:
        logging.error(f"Erro ao pesquisar campanha: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao pesquisar campanha.")


@router.get("/campanha/visualizar-campanhas")
async def visualizar_campanhas(usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            campanhas = await listar_campanhas(db=db)
            return {"status": "success", "campanha": campanhas}
    except HTTPException as e:
        logging.error(f"Erro ao listar campanhas: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar campanhas.")


