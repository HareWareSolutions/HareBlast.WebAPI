import requests


def criar_instancia_jd(nome_instancia, token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/instancias/criarinstancia'
    headers = {
        'tokenCliente': token_cliente,
        'Content-Type': 'application/json'
    }
    payload = {
        "instancia": nome_instancia
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": f"Erro ao criar {e}"}


def configurar_webhook_jd(instancia, url_webhook='https://service-api.hareinteract.com.br/webhook-join', token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/webhook/configurarinstancia'

    headers = {
        'tokenCliente': token_cliente,
        'instancia': instancia
    }

    payload = {
        "url": url_webhook
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.status_code, response.json()


def verificar_status_conexao_jd(instancia: str, token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/instancias/statusconexao'

    headers = {
        'tokenCliente': token_cliente,
        'instancia': instancia
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": str(e)}


def deslogar_instancia_jd(instancia: str, token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/instancias/deslogar'

    headers = {
        'tokenCliente': token_cliente,
        'instancia': instancia
    }

    try:
        response = requests.delete(url, headers=headers, data='')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"erro": str(e)}


def enviar_imagem_jd(instancia, numero, media_base64, nome_arquivo, legenda=None, delay_ms=0,
                  presence="composing", token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/mensagens/enviarimagem'

    headers = {
        'tokenCliente': token_cliente,
        'instancia': instancia
    }

    payload = {
        "number": numero,
        "options": {
            "delay": delay_ms,
            "presence": presence
        },
        "mediaMessage": {
            "mediatype": "image",
            "fileName": nome_arquivo,
            "caption": legenda or "",
            "media": media_base64
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.status_code, response.json()


def enviar_texto_jd(instancia, numero, mensagem, delay_ms=0, presence="composing", token_cliente='ea49bd3e-652d-4cfd-be9d-4aea210d73b0'):
    url = 'https://api-prd.joindeveloper.com.br/mensagens/enviartexto'

    headers = {
        'tokenCliente': token_cliente,
        'instancia': instancia
    }

    payload = {
        "number": numero,
        "options": {
            "delay": delay_ms,
            "presence": presence
        },
        "textMessage": {
            "text": mensagem
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.status_code, response.json()