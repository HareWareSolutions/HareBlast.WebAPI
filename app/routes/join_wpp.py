from fastapi import APIRouter, Depends, HTTPException
from app.auth2.token import get_current_user
from pydantic import BaseModel
from app.services.join_wpp import criar_instancia_jd, verificar_status_conexao_jd, deslogar_instancia_jd, configurar_webhook_jd
from datetime import datetime, date, timedelta
from app.db.db import get_db
from typing import Optional
from app.utils.recupera_empresa import recuperar_empresa
import logging


router = APIRouter()


@router.post("/join_wpp/criar-instancia")
async def criar_instancia(usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f'Erro ao recuperar CNPJ da empresa do usuário: {str(e)}')
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao encontrar CNPJ da empresa correspondente.')

        qr_code = criar_instancia_jd(cnpj_empresa_user)

        return qr_code
    except Exception as e:
        logging.error(f'Erro ao criar instancia do WhatsApp da empresa: {str(e)}')
        return {"status": "error", "message": str(e)}


@router.post("join_wpp/configurar-webhook")
async def configurar_webhook(usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f'Erro ao recuperar CNPJ da empresa do usuário: {str(e)}')
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao CNPJ da empresa correspondente.')

        webhook_return = configurar_webhook_jd(cnpj_empresa_user)

        return webhook_return
    except Exception as e:
        logging.error(f'Erro ao configurar webhook da instancia: {str(e)}')
        return {"status": "error", "message": str(e)}


@router.get("/join_wpp/verificar-status-instancia")
async def recuperar_instancia_jd(usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f"Erro ao recuperar CNPJ da empresa do usuário: {str(e)}")
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao encontrar CNPJ da empresa correspondente.')

        status_instancia = verificar_status_conexao_jd(cnpj_empresa_user)

        return status_instancia
    except Exception as e:
        logging.error(f"Erro ao criar instancia do WhatsApp da empresa: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.delete("/join_wpp/deslogar-instancia")
async def deslogar_instancia_jd_route(usuario_atual: dict = Depends(get_current_user)):
    try:
        try:
            cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        except Exception as e:
            logging.error(f"Erro ao recuperar CNPJ da empresa do usuário: {str(e)}")
            return {"status": "error", "message": str(e)}

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao encontrar CNPJ da empresa correspondente.')

        resultado = deslogar_instancia_jd(cnpj_empresa_user)

        return resultado
    except Exception as e:
        logging.error(f"Erro ao deslogar instancia do WhatsApp da empresa: {str(e)}")
        return {"status": "error", "message": str(e)}