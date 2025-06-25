from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

from app.auth2.token import get_current_user
from app.models.empresa import (
    criar_empresa,
    buscar_empresa_cnpj,
    listar_empresas,
    deletar_empresa_cnpj,
    atualizar_empresa_cnpj
)
from app.db.db import get_db
from app.utils.validador_cnpj import validar_cnpj
from app.utils.transformadores_json import empresa_to_dict
import logging


class EmpresaCreate(BaseModel):
    nome_fantasia: str
    razao_social: str
    cnpj: str
    endereco: str
    telefone: str
    email: str
    status: bool


class EmpresaUpdate(BaseModel):
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[bool] = None


router = APIRouter()


@router.post("/empresa/cadastrar-empresa")
async def cadastrar_empresa(nova_empresa: EmpresaCreate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            data_atual = date.today()

            if not validar_cnpj(nova_empresa.cnpj):
                return {"status": "error", "message": "Cnpj informado é inválido."}

            nova_empresa_obj = await criar_empresa(
                db=db,
                nome_fantasia=nova_empresa.nome_fantasia,
                razao_social=nova_empresa.razao_social,
                cnpj=nova_empresa.cnpj,
                endereco=nova_empresa.endereco,
                telefone=nova_empresa.telefone,
                email=nova_empresa.email,
                data_cadastro=data_atual,
                status=nova_empresa.status
            )

            if nova_empresa_obj is not None:
                nova_empresa_dict = empresa_to_dict(nova_empresa_obj)
                return {"status": "success", "empresa": nova_empresa_dict}
            else:
                return {"status": "error", "message": "Erro ao cadastrar empresa."}
        except Exception as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.delete("/empresa/deletar-empresa/{cnpj}")
async def deletar_empresa(cnpj: str, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            empresa = await buscar_empresa_cnpj(db=db, cnpj=cnpj)
            if empresa:
                sucesso = await deletar_empresa_cnpj(db=db, cnpj=cnpj)
                if sucesso:
                    return {"status": "success"}
                else:
                    return {"status": "error", "message": "Erro ao deletar empresa."}
            else:
                raise HTTPException(status_code=404, detail="Empresa informada não encontrada.")
        except Exception as e:
            logging.error(f"Erro ao processar a requisição {str(e)}")
            return {"status": "error", "message": str(e)}


@router.patch("/empresa/editar-empresa/{cnpj}")
async def editar_empresa(cnpj: str, dados: EmpresaUpdate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            empresa_existente = await buscar_empresa_cnpj(db=db, cnpj=cnpj)
            if not empresa_existente:
                raise HTTPException(status_code=404, detail="Empresa não encontrada.")

            empresa_atualizada = await atualizar_empresa_cnpj(
                db=db,
                nome_fantasia=dados.nome_fantasia,
                razao_social=dados.razao_social,
                cnpj=cnpj,
                endereco=dados.endereco,
                telefone=dados.telefone,
                email=dados.email,
                data_cadastro=None,
                status=dados.status
            )

            if empresa_atualizada:
                return {"status": "success", "empresa": empresa_to_dict(empresa_atualizada)}
            else:
                raise HTTPException(status_code=400, detail="Não foi possível atualizar a empresa.")
        except Exception as e:
            logging.error(f"Erro ao editar empresa: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/empresa/pesquisar-empresa/{cnpj}")
async def visualizar_empresa(cnpj: str, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            empresa = await buscar_empresa_cnpj(db=db, cnpj=cnpj)
            if empresa:
                return {"status": "success", "empresa": empresa_to_dict(empresa)}
            else:
                raise HTTPException(status_code=404, detail="Empresa não encontrada.")
        except Exception as e:
            logging.error(f"Erro ao visualizar empresa: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/empresa/listar")
async def listar_empresas_route(usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            empresas = await listar_empresas(db=db)
            return {"status": "success", "empresas": empresas}
        except Exception as e:
            logging.error(f"Erro ao listar empresas: {str(e)}")
            return {"status": "error", "message": str(e)}
