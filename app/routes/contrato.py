from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth2.token import get_current_user
from app.auth2.security import get_password_hash
from pydantic import BaseModel
from app.models.contrato import criar_contrato, atualizar_contrato, deletar_contrato, buscar_contrato, buscar_contrato_formatado, listar_contratos, buscar_contratos_empresa, buscar_contratos_empresa_formatado, listar_contratos_formatados
from app.db.db import get_db
from datetime import datetime, date, timedelta
from app.utils.transformadores_json import contrato_to_dict
from typing import Optional
import logging


class ContratoCreate(BaseModel):
    empresa_id: int
    plano: int
    tempo_vigencia: int
    status: bool


class ContratoUpdate(BaseModel):
    plano: Optional[int] = None
    tempo_vigencia: Optional[int] = None
    pago: Optional[bool] = None
    status: Optional[bool] = None


router = APIRouter()


@router.post("/contrato/cadastrar-contrato")
async def cadastrar_contrato(novo_contrato: ContratoCreate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            data_atual = date.today()
            data_termino_contrato = data_atual + timedelta(days=novo_contrato.tempo_vigencia)
            try:
                novo_contrato = await criar_contrato(db, novo_contrato.empresa_id, novo_contrato.plano, novo_contrato.tempo_vigencia, data_atual,
                                                   data_termino_contrato, None, False, novo_contrato.status)
            except Exception as e:
                logging.error(f"Erro ao cadastrar contrato: {str(e)}")
                return {"status": "error", "message": str(e)}

            if novo_contrato is not None:
                novo_contrato_dict = contrato_to_dict(novo_contrato)
                return {"status": "success", 'contrato': novo_contrato_dict}
            else:
                logging.error(f"Erro ao cadastrar contrato.")
                return {"status": "error", "message": "Erro ao cadastrar contrato."}
        except Exception as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.delete("/contrato/deletar-contrato/{id_contrato}")
async def deletar_contrato(id_contrato: int, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                contrato = await buscar_contrato(db, id_contrato)
            except Exception as e:
                logging.error(f"Erro ao buscar contrato: {str(e)}")
                return {"status": "error", "message": str(e)}

            if contrato:
                try:
                    sucesso = await deletar_contrato(db, id_contrato)
                except Exception as e:
                    logging.error(f"Erro ao deletar contrato: {str(e)}")
                    return {"status": "error", "message": str(e)}

                if sucesso:
                    return {"status": "success"}
                else:
                    return {"status": "error", "message": "Erro ao deletar contrato"}
            else:
                raise HTTPException(status_code=400, detail="Contrato informado não encontrado.")
        except Exception as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.patch("/contrato/editar-contrato/{id_contrato}")
async def editar_contrato(id_contrato: int, dados: ContratoUpdate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                contrato = await buscar_contrato(db, id_contrato)
            except Exception as e:
                logging.error(f"Erro ao buscar contrato: {str(e)}")
                return {"status": "error", "message": str(e)}

            data_ultimo_pagamento = None
            data_atual = None
            data_termino_contrato = None

            if dados.tempo_vigencia is not None:
                data_atual = date.today()
                data_termino_contrato = data_atual + timedelta(days=dados.tempo_vigencia)
            if dados.pago is not None and dados.pago is True:
                data_ultimo_pagamento = date.today()

            if contrato:
                try:
                    contrato_atualizado = await atualizar_contrato(db, id_contrato, dados.plano, dados.tempo_vigencia, data_atual, data_termino_contrato,
                                                                   data_ultimo_pagamento, dados.pago, dados.status)
                except Exception as e:
                    logging.error(f"Erro ao atualizar contrato: {str(e)}")
                    return {"status": "error", "message": str(e)}

                if contrato_atualizado is not None:
                    contrato_atualizado_dict = contrato_to_dict(contrato_atualizado)
                    return {"status": "success", 'contrato': contrato_atualizado_dict}
                else:
                    return {"status": "error", "message": "Erro ao atualizar contrato."}
            else:
                raise HTTPException(status_code=400, detail="Contrato informado não encontrado.")
        except Exception as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/contrato/pesquisar-contrato/{id_contrato}")
async def pesquisar_contrato(id_contrato: int, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                contrato = await buscar_contrato_formatado(db, id_contrato)
            except Exception as e:
                logging.error(f"Erro ao buscar contrato: {str(e)}")
                return {"status": "error", "message": str(e)}

            if contrato:
                return contrato
            else:
                raise HTTPException(status_code=404, detail="Contrato informado não encontrado")
        except Exception as e:
            logging.error(f"Error ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/contrato/pesquisar-contratos-empresa/{id_empresa}")
async def pesquisar_contrato_empresa(id_empresa: int, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                contratos = await buscar_contratos_empresa_formatado(db, id_empresa)
            except Exception as e:
                logging.error(f"Erro ao buscar contrato {str(e)}")
                return {"status": "error", "message": str(e)}

            if contratos:
                return contratos
            else:
                raise HTTPException(status_code=404, detail="Contratos da empresa não encontrados.")
        except Exception as e:
            logging.error(f"Error ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/contrato/visualizar-contratos")
async def visualizar_contratos_empresa(usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                contratos = await listar_contratos_formatados(db)
            except Exception as e:
                logging.error(f"Erro ao buscar contrato: {str(e)}")
                return {"status": "error", "message": str(e)}

            if contratos:
                return contratos
            else:
                raise HTTPException(status_code=400, detail="Contratos não encontrados.")
        except Exception as e:
            logging.error(f"Error ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}

