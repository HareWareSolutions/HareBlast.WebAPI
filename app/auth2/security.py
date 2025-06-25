from app.models.usuario import buscar_usuario
from app.models.empresa import buscar_empresa
from passlib.context import CryptContext
from app.db.db import get_db
import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    async with get_db('hareware') as db:
        try:
            try:
                user = await buscar_usuario(db, username)
            except Exception as e:
                logging.error(f"Erro ao processar a operação de buscar usuário: {str(e)}")
                return {"status": "error", "message": str(e)}

            if user:
                user_data = {
                    "id": user.id,
                    "usuario": user.usuario,
                    "senha": user.senha,
                    "nivel_acesso": user.nivel_acesso,
                    "empresa": user.id_empresa,
                    "status": user.status
                }

                enterprise = await buscar_empresa(db, user_data['empresa'])

                if enterprise.status is False:
                    return False

                if not verify_password(password, user_data['senha']):
                    return False

                return user_data

        except Exception as e:
            logging.error(f"Erro ao processar a requisição de autenticar usuário: {str(e)}")
            return {"status": "error", "message": str(e)}

