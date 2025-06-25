from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from enum import Enum
from sqlalchemy.orm import relationship
from app.utils.transformadores_json import produto_to_dict
from app.db.db import Base


class UnidadeMedida(str, Enum):
    kg = "kg"
    g = "g"
    mg = "mg"
    ton = "ton"
    l = "l"
    ml = "ml"
    m3 = "m³"
    cm3 = "cm³"
    m = "m"
    cm = "cm"
    mm = "mm"
    unidade = "unidade"
    pacote = "pacote"
    caixa = "caixa"
    duzia = "dúzia"


class Produto(Base):
    __tablename__ = "produto"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    codigo_produto = Column(String, unique=True, nullable=False)
    unidade_medida = Column(String, unique=True, nullable=False)
    preco_venda = Column(Numeric(precision=10, scale=2), nullable=False, default=Decimal('0.00'))
    qtd_estoque = Column(Integer, default=0, nullable=False)
    link = Column(String, nullable=True)

    campanhas_associadas = relationship("CampanhaProduto", back_populates="produto")



async def criar_produto(
    db: AsyncSession,
    nome: str,
    descricao: str,
    codigo_produto: str,
    unidade_medida,
    preco_venda: Decimal,
    qtd_estoque: int,
    link: str
):
    # Converter para Enum se for string
    if isinstance(unidade_medida, str):
        unidade_medida = UnidadeMedida(unidade_medida)

    novo_produto = Produto(
        nome=nome,
        descricao=descricao,
        codigo_produto=codigo_produto,
        unidade_medida=unidade_medida.value,  # <-- aqui, usa .value para salvar string
        preco_venda=preco_venda,
        qtd_estoque=qtd_estoque,
        link=link
    )
    db.add(novo_produto)
    await db.commit()
    await db.refresh(novo_produto)
    return novo_produto


async def atualizar_produto(
    db: AsyncSession,
    produto_id: int,
    nome: str = None,
    descricao: str = None,
    codigo_produto: str = None,
    unidade_medida=None,
    preco_venda: Decimal = None,
    qtd_estoque: int = None,
    link: str = None
):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    produto = result.scalar_one_or_none()

    if produto:
        if nome is not None:
            produto.nome = nome
        if descricao is not None:
            produto.descricao = descricao
        if codigo_produto is not None:
            produto.codigo_produto = codigo_produto
        if unidade_medida is not None:
            if isinstance(unidade_medida, str):
                unidade_medida = UnidadeMedida(unidade_medida)
            produto.unidade_medida = unidade_medida.value  # <-- sempre .value aqui
        if preco_venda is not None:
            produto.preco_venda = preco_venda
        if qtd_estoque is not None:
            produto.qtd_estoque = qtd_estoque
        if link is not None:
            produto.link = link

        await db.commit()
        await db.refresh(produto)
        return produto

    return None


async def listar_produtos(db: AsyncSession):
    result = await db.execute(select(Produto))
    produtos = result.scalars().all()
    return [produto_to_dict(p) for p in produtos]


async def deletar_produto(db: AsyncSession, produto_id: int):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    produto = result.scalar_one_or_none()

    if produto:
        await db.delete(produto)
        await db.commit()
        return True
    return False


async def buscar_produto(db: AsyncSession, produto_id: int):
    result = await db.execute(select(Produto).filter(Produto.id == produto_id))
    return result.scalar_one_or_none()
