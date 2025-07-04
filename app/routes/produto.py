from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.auth2.token import get_current_user
from app.models.produto import (
    criar_produto,
    buscar_produto,
    listar_produtos,
    deletar_produto,
    atualizar_produto
)
from app.db.db import get_db
from app.utils.recupera_empresa import recuperar_empresa
from app.utils.transformadores_json import produto_to_dict
from app.services.supabase_db import upload_base64_image, delete_file
import logging
import base64


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    codigo_produto: Optional[str] = None
    unidade_medida: Optional[str] = None
    preco_venda: Optional[float] = None
    qtd_estoque: Optional[int] = None
    link: Optional[str] = None


router = APIRouter()


# Cadastrar Produto
@router.post("/produto/cadastrar-produto")
async def cadastrar_produto(
    nome: str = Form(...),
    descricao: str = Form(...),
    codigo_produto: str = Form(...),
    unidade_medida: str = Form(...),
    preco_venda: float = Form(...),
    qtd_estoque: int = Form(...),
    link: str = Form(...),
    imagem1: UploadFile = File(...),
    usuario_atual: dict = Depends(get_current_user)
):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])
        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail='Erro ao encontrar o cnpj da empresa correspondente.')

        conteudo_binario_i1 = await imagem1.read()

        imagem1_b64 = base64.b64encode(conteudo_binario_i1).decode("utf-8")

        upload_img1 = await upload_base64_image(
            base64_string=imagem1_b64,
            file_name=imagem1.filename,
            bucket_name="hareblast",
            storage_path=f"produtos/{cnpj_empresa_user}",
            content_type=imagem1.content_type,
            overwrite=True
        )

        async with get_db(cnpj_empresa_user) as db:
            try:
                produto = await criar_produto(
                    db=db,
                    nome=nome,
                    descricao=descricao,
                    codigo_produto=codigo_produto,
                    unidade_medida=unidade_medida,
                    preco_venda=preco_venda,
                    qtd_estoque=qtd_estoque,
                    link=link,
                    url_imagem1=upload_img1['public_url'],
                    url_imagem2=None,
                    url_imagem3=None,
                    path_imagem1=upload_img1['path'],
                    path_imagem2=None,
                    path_imagem3=None
                )
                produto_dict = produto_to_dict(produto)
                return {"status": "success", "produto": produto_dict}
            except Exception as e:
                logging.error(f'Erro ao cadastrar produto: {str(e)}')
                raise HTTPException(status_code=500, detail='Erro ao cadastrar produto.')
    except HTTPException as e:
        logging.info(f"Erro ao processar a requisição: {str(e)}")
        return {"status": "error", "message": str(e.detail)}


# Deletar Produto
@router.delete("/produto/deletar-produto/{id_produto}")
async def deletar_produto_endpoint(id_produto: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produto = await buscar_produto(db, id_produto)

            if produto.url_imagem1:
                resultado_deletar = await delete_file('hareblast', [produto.path_imagem1])
            if produto.url_imagem2:
                resultado_deletar = await delete_file('hareblast', [produto.path_imagem2])
            if produto.url_imagem3:
                resultado_deletar = await delete_file('hareblast', [produto.path_imagem3])

            sucesso = await deletar_produto(db=db, produto_id=id_produto)
            if not sucesso:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")
            return {"status": "success", "message": "Produto deletado com sucesso."}
    except Exception as e:
        logging.error(f"Erro ao deletar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao deletar produto.")


# Atualizar Produto
@router.patch("/produto/atualizar-produto/{id_produto}")
async def atualizar_produto_endpoint(
    id_produto: int,
    nome: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    codigo_produto: Optional[str] = Form(None),
    unidade_medida: Optional[str] = Form(None),
    preco_venda: Optional[float] = Form(None),
    qtd_estoque: Optional[int] = Form(None),
    link: Optional[str] = Form(None),
    imagem1: Optional[UploadFile] = File(None),
    usuario_atual: dict = Depends(get_current_user)
):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:

            if imagem1:
                conteudo_binario_i1 = await imagem1.read()
                imagem1_b64 = base64.b64encode(conteudo_binario_i1).decode("utf-8")

                produto_versao_atual = await buscar_produto(db, id_produto)

                if produto_versao_atual.url_imagem1:
                    resultado_deletar = await delete_file('hareblast', produto_versao_atual.path_imagem1)

                upload_img1 = await upload_base64_image(
                    base64_string=imagem1_b64,
                    file_name=imagem1.filename,
                    bucket_name="hareblast",
                    storage_path=f"produtos/{cnpj_empresa_user}",
                    content_type=imagem1.content_type,
                    overwrite=True
                )

                url_i1 = upload_img1['public_url']
                path_i1 = upload_img1['path']
            else:
                url_i1 = None
                path_i1 = None

            produto_atualizado = await atualizar_produto(
                db=db,
                produto_id=id_produto,
                nome=nome,
                descricao=descricao,
                codigo_produto=codigo_produto,
                unidade_medida=unidade_medida,
                preco_venda=preco_venda,
                qtd_estoque=qtd_estoque,
                link=link,
                url_imagem1=url_i1,
                url_imagem2=None,
                url_imagem3=None,
                path_imagem1=path_i1,
                path_imagem2=None,
                path_imagem3=None
            )

            if not produto_atualizado:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")

            produto_dict = produto_to_dict(produto_atualizado)
            return {"status": "success", "produto": produto_dict}
    except Exception as e:
        logging.error(f"Erro ao atualizar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto.")


# Buscar Produto por ID
@router.get("/produto/buscar-produto/{id_produto}")
async def buscar_produto_endpoint(id_produto: int, usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produto = await buscar_produto(db=db, produto_id=id_produto)
            if not produto:
                raise HTTPException(status_code=404, detail="Produto não encontrado.")
            produto_dict = produto_to_dict(produto)
            return {"status": "success", "produto": produto_dict}
    except Exception as e:
        logging.error(f"Erro ao buscar produto: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar produto.")


# Listar Todos os Produtos
@router.get("/produto/listar-produtos")
async def listar_produtos_endpoint(usuario_atual: dict = Depends(get_current_user)):
    try:
        cnpj_empresa_user = await recuperar_empresa(usuario_atual['username'])

        if not cnpj_empresa_user:
            raise HTTPException(status_code=400, detail="CNPJ da empresa não encontrado.")

        async with get_db(cnpj_empresa_user) as db:
            produtos = await listar_produtos(db=db)
            return {"status": "success", "produtos": produtos}
    except Exception as e:
        logging.error(f"Erro ao listar produtos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar produtos.")
