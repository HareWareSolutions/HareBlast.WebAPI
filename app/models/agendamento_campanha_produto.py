from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from app.db.db import Base


class AgendamentoCampanhaProduto(Base):
    __tablename__ = "agendamento_campanha_produto"

    id = Column(Integer, primary_key=True)
    campanha_produto_id = Column(Integer, ForeignKey("campanha_produto.id"))
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    campanha_produto = relationship("CampanhaProduto", back_populates="campanhas_produtos_associados")


async def criar_agendamento_campanha_produto(
        db: AsyncSession,
        campanha_produto_id: int,
        data: Date,
        hora: Time
):
    novo_agendamento_campanha_produto = AgendamentoCampanhaProduto(
        campanha_produto_id=campanha_produto_id,
        data=data,
        hora=hora
    )

    db.add(novo_agendamento_campanha_produto)
    await db.commit()
    await db.refresh(novo_agendamento_campanha_produto)
    return novo_agendamento_campanha_produto


async def deletar_agendamento_campanha_produto(
        db: AsyncSession,
        agendamento_campanha_produto_id: int
):
    result = await db.execute(
        select(AgendamentoCampanhaProduto).where(AgendamentoCampanhaProduto.id == agendamento_campanha_produto_id)
    )
    agendamento_campanha_produto = result.scalar_one_or_none()

    if agendamento_campanha_produto is None:
        return False

    await db.delete(agendamento_campanha_produto)
    await db.commit()
    return True


async def listar_todos_agendamentos_campanha_produto(db: AsyncSession):
    result = await db.execute(select(AgendamentoCampanhaProduto))
    agendamentos_campanha_produtos = result.scalars().all()
    return [
        {
            "id": agendamento_campanha_produto.id,
            "campanha_produto_id": agendamento_campanha_produto.campanha_produto_id,
            "data": agendamento_campanha_produto.data,
            "hora": agendamento_campanha_produto.hora
        }
        for agendamento_campanha_produto in agendamentos_campanha_produtos
    ]


async def listar_agendamentos_campanha_produto_por_cp(
        db: AsyncSession,
        campanha_produto_id: int
):
    result = await db.execute(
        select(AgendamentoCampanhaProduto).where(AgendamentoCampanhaProduto.campanha_produto_id == campanha_produto_id)
    )
    agendamentos_campanhas_produtos = result.scalars().all()
    return [
        {
            "id": acp.id,
            "campanha_produto_id": acp.campanha_produto_id,
            "data": acp.data,
            "hora": acp.hora
        }
        for acp in agendamentos_campanhas_produtos
    ]
