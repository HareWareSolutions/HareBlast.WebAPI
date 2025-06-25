from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from fastapi import HTTPException
from app.utils.transformadores_json import contrato_to_dict
from app.db.db import Base


class Contrato(Base):
    __tablename__ = "contrato"

    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("empresa.id"), nullable=False)
    plano = Column(Integer, nullable=False)
    tempo_vigencia = Column(Integer, nullable=False)
    inicio_contrato = Column(Date, nullable=False)
    termino_contrato = Column(Date, nullable=False)
    data_ultimo_pagamento = Column(Date, nullable=True)
    pago = Column(Boolean, nullable=False, default=False)
    status = Column(Boolean, nullable=False, default=True)

    empresa = relationship("Empresa")


async def criar_contrato(
        db: AsyncSession,
        empresa_id: int,
        plano: int,
        tempo_vigencia: int,
        inicio_contrato,
        termino_contrato,
        data_ultimo_pagamento,
        pago: bool,
        status: bool
):
    novo_contrato = Contrato(
        empresa_id=empresa_id,
        plano=plano,
        tempo_vigencia=tempo_vigencia,
        inicio_contrato=inicio_contrato,
        termino_contrato=termino_contrato,
        data_ultimo_pagamento=data_ultimo_pagamento,
        pago=pago,
        status=status
    )

    db.add(novo_contrato)
    await db.commit()
    await db.refresh(novo_contrato)
    return novo_contrato


async def atualizar_contrato(
        db: AsyncSession,
        contrato_id: int,
        plano: int = None,
        tempo_vigencia: int = None,
        inicio_contrato = None,
        termino_contrato = None,
        data_ultimo_pagamento = None,
        pago: bool = None,
        status: bool = None
):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    contrato = result.scalar_one_or_none()

    if contrato:
        if plano is not None:
            contrato.plano = plano
        if tempo_vigencia is not None:
            contrato.tempo_vigencia = tempo_vigencia
        if inicio_contrato is not None:
            contrato.inicio_contrato = inicio_contrato
        if termino_contrato is not None:
            contrato.termino_contrato = termino_contrato
        if data_ultimo_pagamento is not None:
            contrato.data_ultimo_pagamento = data_ultimo_pagamento
        if pago is not None:
            contrato.pago = pago
        if status is not None:
            contrato.status = status

        await db.commit()
        await db.refresh(contrato)
        return contrato
    return None


async def listar_contratos(db: AsyncSession):
    result = await db.execute(select(Contrato))
    return result.scalars().all()


async def listar_contratos_formatados(db: AsyncSession):
    result = await db.execute(select(Contrato))
    contratos = result.scalars().all()

    return [
        {
            "id": c.id,
            "empresa_id": c.empresa_id,
            "plano": c.plano,
            "tempo_vigencia": c.tempo_vigencia,
            "inicio_contrato": c.inicio_contrato.isoformat() if c.inicio_contrato else None,
            "termino_contrato": c.termino_contrato.isoformat() if c.termino_contrato else None,
            "data_ultimo_pagamento": c.data_ultimo_pagamento.isoformat() if c.data_ultimo_pagamento else None,
            "pago": c.pago,
            "status": c.status,
        }
        for c in contratos
    ]



async def deletar_contrato(db: AsyncSession, contrato_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    contrato = result.scalar_one_or_none()

    if contrato:
        await db.delete(contrato)
        await db.commit()
        return True
    return False


async def buscar_contrato(db: AsyncSession, contrato_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    return result.scalar_one_or_none()


async def buscar_contrato_formatado(db: AsyncSession, contrato_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.id == contrato_id))
    contrato = result.scalar_one_or_none()

    if contrato is None:
        return None

    return {
        "id": contrato.id,
        "empresa_id": contrato.empresa_id,
        "plano": contrato.plano,
        "tempo_vigencia": contrato.tempo_vigencia,
        "inicio_contrato": contrato.inicio_contrato.isoformat() if contrato.inicio_contrato else None,
        "termino_contrato": contrato.termino_contrato.isoformat() if contrato.termino_contrato else None,
        "data_ultimo_pagamento": contrato.data_ultimo_pagamento.isoformat() if contrato.data_ultimo_pagamento else None,
        "pago": contrato.pago,
        "status": contrato.status,
    }


async def buscar_contratos_empresa(db: AsyncSession, empresa_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.empresa_id == empresa_id))
    return result.scalars().all()


async def buscar_contratos_empresa_formatado(db: AsyncSession, empresa_id: int):
    result = await db.execute(select(Contrato).filter(Contrato.empresa_id == empresa_id))
    contratos = result.scalars().all()

    return [
        {
            "id": c.id,
            "empresa_id": c.empresa_id,
            "plano": c.plano,
            "tempo_vigencia": c.tempo_vigencia,
            "inicio_contrato": c.inicio_contrato.isoformat() if c.inicio_contrato else None,
            "termino_contrato": c.termino_contrato.isoformat() if c.termino_contrato else None,
            "data_ultimo_pagamento": c.data_ultimo_pagamento.isoformat() if c.data_ultimo_pagamento else None,
            "pago": c.pago,
            "status": c.status,
        }
        for c in contratos
    ]

