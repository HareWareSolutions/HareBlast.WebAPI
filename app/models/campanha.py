from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from app.db.db import Base


class Campanha(Base):
    __tablename__ = "campanha"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    inicio_campanha = Column(Date, nullable=False)
    fim_campanha = Column(Date, nullable=False)

    produtos_associados = relationship(
        "CampanhaProduto",
        back_populates="campanha",
        cascade="all, delete-orphan"
    )


async def criar_campanha(
        db: AsyncSession,
        nome: str,
        inicio_campanha,
        fim_campanha
):
    nova_campanha = Campanha(
        nome=nome,
        inicio_campanha=inicio_campanha,
        fim_campanha=fim_campanha
    )

    db.add(nova_campanha)
    await db.commit()
    await db.refresh(nova_campanha)
    return nova_campanha


async def atualizar_campanha(
        db: AsyncSession,
        campanha_id: int,
        nome: str = None,
        inicio_campanha = None,
        fim_campanha = None
):
    result = await db.execute(select(Campanha).filter(Campanha.id == campanha_id))
    campanha = result.scalar_one_or_none()

    if campanha:
        if nome is not None:
            campanha.nome = nome
        if inicio_campanha is not None:
            campanha.inicio_campanha = inicio_campanha
        if fim_campanha is not None:
            campanha.fim_campanha = fim_campanha

        await db.commit()
        await db.refresh(campanha)
        return campanha
    return None


async def deletar_campanha(
        db: AsyncSession,
        campanha_id: int
):
    result = await db.execute(select(Campanha).where(Campanha.id == campanha_id))
    campanha = result.scalar_one_or_none()

    if campanha is None:
        return False

    await db.delete(campanha)
    await db.commit()
    return True


async def listar_campanhas(db: AsyncSession):
    result = await db.execute(select(Campanha))
    campanhas = result.scalars().all()
    return [
        {
            "id": campanha.id,
            "nome": campanha.nome,
            "inicio_campanha": campanha.inicio_campanha,
            "fim_campanha": campanha.fim_campanha
        }
        for campanha in campanhas
    ]


async def buscar_campanha_por_id(db: AsyncSession, campanha_id: int):
    result = await db.execute(select(Campanha).where(Campanha.id == campanha_id))
    campanha = result.scalar_one_or_none()
    return campanha
