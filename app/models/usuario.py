from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from app.db.db import Base
from app.utils.transformadores_json import usuario_to_dict


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    usuario = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    nivel_acesso = Column(Integer, nullable=False)
    ultimo_acesso = Column(Date, nullable=True)
    data_cadastro = Column(Date, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    id_empresa = Column(Integer, ForeignKey("empresa.id"), nullable=False)

    empresa = relationship("Empresa")


async def criar_usuario(
        db: AsyncSession,
        nome: str,
        usuario: str,
        email: str,
        telefone: str,
        senha: str,
        nivel_acesso: int,
        ultimo_acesso,
        data_cadastro,
        status: bool,
        id_empresa: int
):
    novo_usuario = Usuario(
        nome=nome,
        usuario=usuario,
        email=email,
        telefone=telefone,
        senha=senha,
        nivel_acesso=nivel_acesso,
        ultimo_acesso=ultimo_acesso,
        data_cadastro=data_cadastro,
        status=status,
        id_empresa=id_empresa
    )

    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)
    return novo_usuario


async def atualizar_usuario(
        db: AsyncSession,
        usuario_id: int,
        nome: str = None,
        usuario: str = None,
        email: str = None,
        telefone: str = None,
        senha: str = None,
        nivel_acesso: int = None,
        ultimo_acesso = None,
        data_cadastro = None,
        status: bool = None
):
    result = await db.execute(select(Usuario).filter(Usuario.id == usuario_id))
    usuario_data = result.scalar_one_or_none()

    if usuario_data:
        if nome is not None:
            usuario_data.nome = nome
        if usuario is not None:
            usuario_data.usuario = usuario
        if email is not None:
            usuario_data.email = email
        if telefone is not None:
            usuario_data.telefone = telefone
        if senha is not None:
            usuario_data.senha = senha
        if nivel_acesso is not None:
            usuario_data.nivel_acesso = nivel_acesso
        if ultimo_acesso is not None:
            usuario_data.ultimo_acesso = ultimo_acesso
        if data_cadastro is not None:
            usuario_data.data_cadastro = data_cadastro
        if status is not None:
            usuario_data.status = status

        await db.commit()
        await db.refresh(usuario_data)
        return usuario_data
    return None


async def listar_usuarios(db: AsyncSession):
    result = await db.execute(select(Usuario))
    return result.scalars().all()


async def deletar_usuario(db: AsyncSession, username: str):
    result = await db.execute(select(Usuario).filter(Usuario.usuario == username))
    usuario = result.scalar_one_or_none()

    if usuario:
        await db.delete(usuario)
        await db.commit()
        return True
    return False


async def buscar_usuario(db: AsyncSession, usuario: str):
    result = await db.execute(select(Usuario).filter(Usuario.usuario == usuario))
    return result.scalar_one_or_none()


async def buscar_usuarios_empresa(db: AsyncSession, empresa_id: int):
    result = await db.execute(select(Usuario).filter(Usuario.id_empresa == empresa_id))
    usuarios = result.scalars().all()
    return [usuario_to_dict(u) for u in usuarios]


async def buscar_usuario_id(db: AsyncSession, usuario_id: int):
    result = await db.execute(select(Usuario).filter(Usuario.id == usuario_id))
    return result.scalar_one_or_none()
