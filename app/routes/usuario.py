from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth2.token import get_current_user
from app.auth2.security import get_password_hash
from pydantic import BaseModel, EmailStr
from app.models.usuario import buscar_usuario, buscar_usuarios_empresa, criar_usuario, deletar_usuario, atualizar_usuario
from app.models.empresa import buscar_empresa
from app.models.contrato import buscar_contratos_empresa
from app.db.db import get_db
from datetime import datetime, date
from app.utils.verificar_planos import verificar_planos_contrato
from app.utils.transformadores_json import usuario_to_dict
from typing import Optional
import logging


class UsuarioCreate(BaseModel):
    nome: str
    username: str
    email: EmailStr
    telefone: str
    senha: str
    nivel_acesso: int
    codigo_empresa: int


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None
    nivel_acesso: Optional[int] = None
    status: Optional[bool] = None


router = APIRouter()


@router.post("/usuario/cadastrar-usuario")
async def cadastrar_usuario(novo_usuario: UsuarioCreate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                usuario = await buscar_usuario(db, novo_usuario.username)
            except Exception as e:
                logging.error(f"Erro ao processar a operação de buscar usuário: {str(e)}")
                return {"status": "error", "message": str(e)}

            if usuario:
                raise HTTPException(status_code=400, detail="Usuário já existe")

            try:
                empresa = await buscar_empresa(db, novo_usuario.codigo_empresa)
            except Exception as e:
                logging.error(f"Erro ao processar a operação de buscar empresa: {str(e)}")
                return {"status": "error", "message": str(e)}

            if empresa:
                try:
                    contratos = await buscar_contratos_empresa(db, empresa.id)
                    contrato = contratos[0]
                except Exception as e:
                    logging.error(f"Erro ao processar a operação de buscar contrato pelo código de Empresa: {str(e)}")
                    return {"status": "error", "message": str(e)}

                quantidade_usuarios_permitido = verificar_planos_contrato(contrato.plano)

                try:
                    usuarios_empresa = await buscar_usuarios_empresa(db, empresa.id)
                except Exception as e:
                    logging.error(f"Erro ao processar a operação de buscar usuarios pelo código de Empresa: {str(e)}")
                    return {"status": "error", "message": str(e)}

                quantidade_usuarios_cadastrados = len(usuarios_empresa)

                if quantidade_usuarios_cadastrados >= quantidade_usuarios_permitido:
                    return {"status": "error", "message": f"Essa Empresa já atingiu o limite de usuários cadastrados."}

                data_atual = date.today()

                if novo_usuario.senha is not None:
                    senha_hash = get_password_hash(novo_usuario.senha)
                else:
                    senha_hash = None
                status = 1
                try:
                    usuario = await criar_usuario(db, novo_usuario.nome, novo_usuario.username, novo_usuario.email, novo_usuario.telefone, senha_hash, novo_usuario.nivel_acesso,
                                                  None, data_atual, status, empresa.id)
                    usuario_dict = usuario_to_dict(usuario)
                    return {"status": "success", 'usuario': usuario_dict}
                except Exception as e:
                    logging.error(f"Erro ao processar a operação de criar um novo usuário no banco: {str(e)}")
                    return {"status": "error", "message": str(e)}
            else:
                raise HTTPException(status_code=400, detail="Empresa informada não encontrada")
        except Exception as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.delete("/usuario/excluir_usuario/{username}")
async def excluir_usuario(username: str, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                usuario = await buscar_usuario(db, username)
            except Exception as e:
                logging.error(f"Erro ao buscar usuário: {str(e)}")
                return {"status": "error", "message": str(e)}

            if usuario:
                try:
                    sucesso = await deletar_usuario(db, usuario.usuario)
                except Exception as e:
                    logging.error(f"Erro ao deletar usuário: {str(e)}")
                    return {"status": "error", "message": str(e)}

                if sucesso:
                    return {"status": "success"}
                else:
                    return {"status": "erro", "message": "Erro ao tentar deletar usuário."}
            else:
                raise HTTPException(status_code=400, detail="Usuário não encontrado.")
        except Exception as e:
            logging.error(f"Erro ao processar a requisição {str(e)}")
            return {"status": "error", "message": str(e)}


@router.patch("/usuario/editar_usuario/{username}")
async def editar_usuario(username: str, dados: UsuarioUpdate, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                usuario = await buscar_usuario(db, username)
            except Exception as e:
                logging.error(f"Erro ao buscar usuário: {str(e)}")
                return {"status": "error", "message": str(e)}

            if usuario:
                if dados.username is not None:
                    try:
                        username_existente = await buscar_usuario(db, dados.username)
                    except Exception as e:
                        logging.error(f"Erro ao buscar usuário: {str(e)}")
                        return {"status": "error", "message": str(e)}

                    if username_existente:
                        raise HTTPException(status_code=409, detail="Já existe um usuário com esse nome.")

                if dados.senha is not None:
                    senha_hash = get_password_hash(dados.senha)
                else:
                    senha_hash = None

                try:
                    usuario_atualizado = await atualizar_usuario(db, usuario.id, dados.nome, dados.username, dados.email, dados.telefone, senha_hash, dados.nivel_acesso, None, None, dados.status)
                except Exception as e:
                    logging.error(f"Erro ao atualizar o usuário: {str(e)}")
                    return {"status": "error", "message": str(e)}

                if usuario_atualizado is not None:
                    usuario_atualizado_dict = usuario_to_dict(usuario_atualizado)
                    return {"status": "success", 'usuario': usuario_atualizado_dict}
                else:
                    return {"status": "error", "message": "Erro ao atualizar o usuário."}
            else:
                raise HTTPException(status_code=400, detail="Usuário não encontrado.")
        except HTTPException as e:
            logging.error(f"Erro ao processar a requisição: {str(e)}")
            return {"status": "error", "message": str(e)}


@router.get("/usuarios/listar_usuarios_empresa/{id_empresa}")
async def listar_usuarios_empresa(id_empresa: int, usuario_atual: dict = Depends(get_current_user)):
    async with get_db('hareware') as db:
        try:
            try:
                empresa = await buscar_empresa(db, id_empresa)
            except Exception as e:
                logging.error(f"Erro ao buscar empresa: {str(e)}")
                return {"status": "error", "message": str(e)}

            if empresa:
                try:
                    usuarios_empresa = await buscar_usuarios_empresa(db, id_empresa)
                except Exception as e:
                    logging.error(f"Erro ao obter usuários de empresa {str(e)}")
                    return {"status": "error", "message": str(e)}

                if usuarios_empresa:
                    return usuarios_empresa
                else:
                    return {"status": "erro", "message": "Erro ao obter usuários de empresa."}
            else:
                raise HTTPException(status_code=400, detail="Empresa não encontrada")
        except Exception as e:
            logging.error(f"Erro ao processar requisição: {str(e)}")
            return {"status": "error", "message": str(e)}






