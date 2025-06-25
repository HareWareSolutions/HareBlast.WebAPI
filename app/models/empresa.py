from typing import Optional
from datetime import date
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils.transformadores_json import empresa_to_dict
from app.db.db import Base


class Empresa(Base):
    __tablename__ = "empresa"

    id = Column(Integer, primary_key=True)
    nome_fantasia = Column(String, nullable=False)
    razao_social = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
    endereco = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    data_cadastro = Column(Date, nullable=True)
    status = Column(Boolean, nullable=False, default=True)  # Se precisar, use server_default='true'


async def criar_empresa(
    db: AsyncSession,
    nome_fantasia: str,
    razao_social: str,
    cnpj: str,
    endereco: str,
    telefone: str,
    email: str,
    data_cadastro: Optional[date] = None,
    status: bool = True
) -> Empresa:
    nova_empresa = Empresa(
        nome_fantasia=nome_fantasia,
        razao_social=razao_social,
        cnpj=cnpj,
        endereco=endereco,
        telefone=telefone,
        email=email,
        data_cadastro=data_cadastro,
        status=status
    )
    db.add(nova_empresa)
    await db.commit()
    await db.refresh(nova_empresa)
    return nova_empresa


async def atualizar_empresa(
    db: AsyncSession,
    empresa_id: int,
    nome_fantasia: Optional[str] = None,
    razao_social: Optional[str] = None,
    cnpj: Optional[str] = None,
    endereco: Optional[str] = None,
    telefone: Optional[str] = None,
    email: Optional[str] = None,
    data_cadastro: Optional[date] = None,
    status: Optional[bool] = None
) -> Optional[Empresa]:
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    empresa = result.scalar_one_or_none()

    if empresa:
        if nome_fantasia is not None:
            empresa.nome_fantasia = nome_fantasia
        if razao_social is not None:
            empresa.razao_social = razao_social
        if cnpj is not None:
            empresa.cnpj = cnpj
        if endereco is not None:
            empresa.endereco = endereco
        if telefone is not None:
            empresa.telefone = telefone
        if email is not None:
            empresa.email = email
        if data_cadastro is not None:
            empresa.data_cadastro = data_cadastro
        if status is not None:
            empresa.status = status

        await db.commit()
        await db.refresh(empresa)
        return empresa
    return None


async def atualizar_empresa_cnpj(
    db: AsyncSession,
    nome_fantasia: Optional[str] = None,
    razao_social: Optional[str] = None,
    cnpj: Optional[str] = None,
    endereco: Optional[str] = None,
    telefone: Optional[str] = None,
    email: Optional[str] = None,
    data_cadastro: Optional[date] = None,
    status: Optional[bool] = None
) -> Optional[Empresa]:
    if cnpj is None:
        return None

    result = await db.execute(select(Empresa).where(Empresa.cnpj == cnpj))
    empresa = result.scalar_one_or_none()

    if empresa:
        if nome_fantasia is not None:
            empresa.nome_fantasia = nome_fantasia
        if razao_social is not None:
            empresa.razao_social = razao_social
        if endereco is not None:
            empresa.endereco = endereco
        if telefone is not None:
            empresa.telefone = telefone
        if email is not None:
            empresa.email = email
        if data_cadastro is not None:
            empresa.data_cadastro = data_cadastro
        if status is not None:
            empresa.status = status

        await db.commit()
        await db.refresh(empresa)
        return empresa
    return None


async def listar_empresas(db: AsyncSession):
    result = await db.execute(select(Empresa))
    empresas = result.scalars().all()
    return [empresa_to_dict(e) for e in empresas]


async def deletar_empresa(db: AsyncSession, empresa_id: int) -> bool:
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    empresa = result.scalar_one_or_none()

    if empresa:
        await db.delete(empresa)
        await db.commit()
        return True
    return False


async def deletar_empresa_cnpj(db: AsyncSession, cnpj: str) -> bool:
    result = await db.execute(select(Empresa).where(Empresa.cnpj == cnpj))
    empresa = result.scalar_one_or_none()

    if empresa:
        await db.delete(empresa)
        await db.commit()
        return True
    return False


async def buscar_empresa(db: AsyncSession, empresa_id: int) -> Optional[Empresa]:
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    return result.scalar_one_or_none()


async def buscar_empresa_cnpj(db: AsyncSession, cnpj: str) -> Optional[Empresa]:
    result = await db.execute(select(Empresa).where(Empresa.cnpj == cnpj))
    return result.scalar_one_or_none()
