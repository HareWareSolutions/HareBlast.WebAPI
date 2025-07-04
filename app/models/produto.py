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
    url_imagem1 = Column(String, nullable=True)
    url_imagem2 = Column(String, nullable=True)
    url_imagem3 = Column(String, nullable=True)
    path_imagem1 = Column(String, nullable=True)
    path_imagem2 = Column(String, nullable=True)
    path_imagem3 = Column(String, nullable=True)

    campanhas_associadas = relationship("CampanhaProduto", back_populates="produto")


async def criar_produto(
    db: AsyncSession,
    nome: str,
    descricao: str,
    codigo_produto: str,
    unidade_medida,
    preco_venda: Decimal,
    qtd_estoque: int,
    link: str,
    url_imagem1: str,
    url_imagem2: str,
    url_imagem3: str,
    path_imagem1: str,
    path_imagem2: str,
    path_imagem3: str
):
    if isinstance(unidade_medida, str):
        unidade_medida = UnidadeMedida(unidade_medida)

    novo_produto = Produto(
        nome=nome,
        descricao=descricao,
        codigo_produto=codigo_produto,
        unidade_medida=unidade_medida.value,
        preco_venda=preco_venda,
        qtd_estoque=qtd_estoque,
        link=link,
        url_imagem1=url_imagem1,
        url_imagem2=url_imagem2,
        url_imagem3=url_imagem3,
        path_imagem1=path_imagem1,
        path_imagem2=path_imagem2,
        path_imagem3=path_imagem3
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
    link: str = None,
    url_imagem1: str = None,
    url_imagem2: str = None,
    url_imagem3: str = None,
    path_imagem1: str = None,
    path_imagem2: str = None,
    path_imagem3: str = None
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
            produto.unidade_medida = unidade_medida.value
        if preco_venda is not None:
            produto.preco_venda = preco_venda
        if qtd_estoque is not None:
            produto.qtd_estoque = qtd_estoque
        if link is not None:
            produto.link = link
        if url_imagem1 is not None:
            produto.url_imagem1 = url_imagem1
        if url_imagem2 is not None:
            produto.url_imagem2 = url_imagem2
        if url_imagem3 is not None:
            produto.url_imagem3 = url_imagem3
        if path_imagem1 is not None:
            produto.path_imagem1 = path_imagem1
        if path_imagem2 is not None:
            produto.path_imagem2 = path_imagem2
        if path_imagem3 is not None:
            produto.path_imagem = path_imagem3

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
