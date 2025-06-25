from app.db.db import get_db
from app.models.usuario import buscar_usuario
from app.models.empresa import buscar_empresa
from fastapi import HTTPException
import logging


async def recuperar_empresa(username: str):
    async with get_db('hareware') as db:
        try:
            try:
                usuario = await buscar_usuario(db, username)
            except Exception as e:
                logging.error(f'Erro ao buscar usuário: {str(e)}')
                raise HTTPException(status_code=500, detail=str(e))

            if usuario:
                try:
                    empresa = await buscar_empresa(db, usuario.id_empresa)
                except Exception as e:
                    logging.error(f'Erro ao buscar empresa: {str(e)}')
                    raise HTTPException(status_code=500, detail=str(e))

                if empresa:
                    return empresa.cnpj
                else:
                    raise HTTPException(status_code=400, detail='Empresa não encontrada')

            else:
                raise HTTPException(status_code=400, detail='Usuário não encontrado.')
        except Exception as e:
            logging.error(f'Erro ao recuperar empresa: {str(e)}')
            raise HTTPException(status_code=400, detail=str(e))
