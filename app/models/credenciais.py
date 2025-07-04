from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal
from sqlalchemy.orm import relationship
from app.db.db import Base


class Credencial(Base):
    __tablename__ = 'credencial'

    id = Column(Integer, primary_key=True)
    identificador_textual = Column(String, nullable=False, unique=True)
    url_api = Column(String, nullable=True)
    token_api = Column(String, nullable=True)
    instancia = Column(String, nullable=True)
    assistant_id = Column(String, nullable=True)


async def criar_credencial(
        db: AsyncSession,
        identificador_textual: str,
        url_api: str,
        token_api: str,
        instancia: str,
        assistant_id: str
):
    nova_credencial = Credencial(
        identificador_textual=identificador_textual,
        url_api=url_api,
        token_api=token_api,
        instancia=instancia,
        assistant_id=assistant_id
    )

    db.add(nova_credencial)
    await db.commit()
    await db.refresh(nova_credencial)
    return nova_credencial


async def atualizar_credencial(
        db: AsyncSession,
        identificador_textual: str,
        url_api: str = None,
        token_api: str = None,
        instancia: str = None,
        assistant_id: str = None
):
    result = await db.execute(select(Credencial).filter(Credencial.identificador_textual == identificador_textual))
    credencial = result.scalar_one_or_none()

    if credencial:
        if url_api is not None:
            credencial.url_api = url_api
        if token_api is not None:
            credencial.token_api = token_api
        if instancia is not None:
            credencial.instancia = instancia
        if assistant_id is not None:
            credencial.assistant_id = assistant_id

        await db.commit()
        await db.refresh(credencial)
        return credencial
    return None


async def deletar_credencial(
        db: AsyncSession,
        identificador_textual: str
):
    result = await db.execute(select(Credencial).filter(Credencial.identificador_textual == identificador_textual))
    credencial = result.scalar_one_or_none()

    if credencial:
        await db.delete(credencial)
        await db.commit()
        return True
    return False


async def listar_credenciais(
        db: AsyncSession
):
    result = await db.execute(select(Credencial))
    return result.scalars().all()


async def buscar_credencial(
        db: AsyncSession,
        identificador_textual: str
):
    result = await db.execute(select(Credencial).filter(Credencial.identificador_textual == identificador_textual))
    return result.scalar_one_or_none()
