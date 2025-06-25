from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from decimal import Decimal
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.routes import campanha_produto


class CampanhaProduto(Base):
    __tablename__ = 'campanha_produto'

    id = Column(Integer, primary_key=True)

    campanha_id = Column(Integer, ForeignKey("campanha.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produto.id"), nullable=False)

    valor_promocional = Column(Numeric(precision=10, scale=2), nullable=False, default=Decimal('0.00'))
    frequencia_exibicao = Column(Integer, nullable=False)

    campanha = relationship("Campanha", back_populates="produtos_associados")
    produto = relationship("Produto", back_populates="campanhas_associadas")


async def criar_campanha_produto(
        db: AsyncSession,
        campanha_id: int,
        produto_id: int,
        valor_promocional: float,
        frequencia_exibicao: int
):
    nova_campanha_produto = CampanhaProduto(
        campanha_id=campanha_id,
        produto_id=produto_id,
        valor_promocional=valor_promocional,
        frequencia_exibicao=frequencia_exibicao
    )

    db.add(nova_campanha_produto)
    await db.commit()
    await db.refresh(nova_campanha_produto)
    return nova_campanha_produto


async def atualizar_campanha_produto(
        db: AsyncSession,
        campanha_produto_id: int,
        campanha_id: int = None,
        produto_id: int = None,
        valor_promocional: float = None,
        frequencia_exibicao: int = None
):
    result = await db.execute(select(CampanhaProduto).filter(CampanhaProduto.id == campanha_produto_id))
    campanha_produto = result.scalar_one_or_none()

    if campanha_produto:
        if campanha_id is not None:
            campanha_produto.campanha_id = campanha_id
        if produto_id is not None:
            campanha_produto.produto_id = produto_id
        if valor_promocional is not None:
            campanha_produto.valor_promocional = valor_promocional
        if frequencia_exibicao is not None:
            campanha_produto.frequencia_exibicao = frequencia_exibicao

        await db.commit()
        await db.refresh(campanha_produto)
        return campanha_produto
    return None


async def deletar_campanha_produto(
        db: AsyncSession,
        campanha_produto_id: int
):
    result = await db.execute(
        select(CampanhaProduto).where(CampanhaProduto.id == campanha_produto_id)
    )
    campanha_produto = result.scalar_one_or_none()

    if campanha_produto is None:
        return False

    await db.delete(campanha_produto)
    await db.commit()
    return True


async def listar_todos_campanha_produto(db: AsyncSession):
    result = await db.execute(select(CampanhaProduto))
    campanhas_produtos = result.scalars().all()
    return [
        {
            "id": campanha_produto.id,
            "campanha_id": campanha_produto.campanha_id,
            "produto_id": campanha_produto.produto_id,
            "valor_promocional": campanha_produto.valor_promocional,
            "frequencia_exibicao": campanha_produto.frequencia_exibicao
        }
        for campanha_produto in campanhas_produtos
    ]


async def listar_campanha_produto_por_campanha(
    db: AsyncSession,
    campanha_id: int
):
    result = await db.execute(
        select(CampanhaProduto).where(CampanhaProduto.campanha_id == campanha_id)
    )
    campanhas_produtos = result.scalars().all()
    return [
        {
            "id": cp.id,
            "campanha_id": cp.campanha_id,
            "produto_id": cp.produto_id,
            "valor_promocional": cp.valor_promocional,
            "frequencia_exibicao": cp.frequencia_exibicao
        }
        for cp in campanhas_produtos
    ]


async def listar_campanha_produto_por_produto(
    db: AsyncSession,
    produto_id: int
):
    result = await db.execute(
        select(CampanhaProduto).where(CampanhaProduto.produto_id == produto_id)
    )
    campanhas_produtos = result.scalars().all()
    return [
        {
            "id": cp.id,
            "campanha_id": cp.campanha_id,
            "produto_id": cp.produto_id,
            "valor_promocional": cp.valor_promocional,
            "frequencia_exibicao": cp.frequencia_exibicao
        }
        for cp in campanhas_produtos
    ]

