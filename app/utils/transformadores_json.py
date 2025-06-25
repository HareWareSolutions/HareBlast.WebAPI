def usuario_to_dict(usuario):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "usuario": usuario.usuario,
        "email": usuario.email,
        "telefone": usuario.telefone,
        "nivel_acesso": usuario.nivel_acesso,
        "ultimo_acesso": usuario.ultimo_acesso.isoformat() if usuario.ultimo_acesso else None,
        "data_cadastro": usuario.data_cadastro.isoformat(),
        "status": usuario.status,
    }


def empresa_to_dict(empresa):
    return {
        "id": empresa.id,
        "nome_fantasia": empresa.nome_fantasia,
        "razao_social": empresa.razao_social,
        "cnpj": empresa.cnpj,
        "endereco": empresa.endereco,
         "telefone": empresa.telefone,
        "email": empresa.email,
        "data_cadastro": empresa.data_cadastro,
        "status": empresa.status
    }


def contrato_to_dict(contrato):
    return {
        "id": contrato.id,
        "empresa": contrato.empresa,
        "plano": contrato.plano,
        "tempo_vigencia": contrato.tempo_vigencia,
        "inicio_contrato": contrato.inicio_contrato,
        "termino_contrato": contrato.termino_contrato,
        "data_ultimo_pagamento": contrato.data_ultimo_pagamento,
        "pago": contrato.pago,
        "status": contrato.status
    }


def produto_to_dict(produto):
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "codigo_produto": produto.codigo_produto,
        "unidade_medida": produto.unidade_medida,
        "preco_venda": produto.preco_venda,
        "qtd_estoque": produto.qtd_estoque,
        "link": produto.link
    }


def campanha_to_dict(campanha):
    return {
        "id": campanha.id,
        "nome": campanha.nome,
        "inicio_campanha": campanha.inicio_campanha,
        "fim_campanha": campanha.fim_campanha
    }


def campanha_produto_to_dict(campanha_produto):
    return {
        "id": campanha_produto.id,
        "campanha_id": campanha_produto.campanha_id,
        "produto_id": campanha_produto.produto_id,
        "valor_promocional": campanha_produto.valor_promocional,
        "frequencia_exibicao": campanha_produto.frequencia_exibicao
    }