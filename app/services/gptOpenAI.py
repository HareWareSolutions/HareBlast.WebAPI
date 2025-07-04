from openai import OpenAI
import requests
import json
from app.db.db import get_db
from app.models.credenciais import buscar_credencial


async def get_credentials(code):
    async with get_db('hareware') as db:
        try:
            credencial = await buscar_credencial(db, code)
            return credencial.token_api, credencial.assistant_id, credencial.instancia
        except Exception as e:
            return f"Erro ao buscar contrato: {str(e)}"


async def ask_to_openai(pergunta, env, id_contato):
    try:
        api_key, assistant_id, thread_id_hw = await get_credentials('openaiHW')

        client = OpenAI(api_key=api_key)

        if thread_id_hw is None:
            thread = client.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = thread_id_hw

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=pergunta
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            latest_message = messages.data[0]

            if hasattr(latest_message, "content") and latest_message.content[0].type == "text":
                return latest_message.content[0].text.value, thread_id
            elif hasattr(latest_message, "content") and latest_message.content[0].type == "function_call":
                function_call = latest_message.content[0].function_call
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)

                #if function_name == "suporte_humano":
                #    print('Entrei no suporte humano')
                #    reason = function_args.get("reason", "Motivo não especificado.")
                #    resposta = await suporte_humano(env, id_contato, reason)
                #    print(resposta)
                #    return resposta, thread_id
                #else:
                #    return f"Função desconhecida: {function_name}", thread_id

            return messages.data[0].content[0].text.value, thread_id
        elif run.status == "failed":
            return "Desculpa, mas meu sistema cognitivo falhou. Poderia escrever novamente sua mensagem?", thread_id
        elif run.status == "incomplete":
            return "Desculpa, não consegui compreender. Poderia reformular sua pergunta?"
        else:
            return f"Erro: {run.status}", thread_id

    except requests.exceptions.Timeout:
        return "Erro de conexão: O tempo de espera pela resposta da API excedeu o limite.", thread_id
    except requests.exceptions.RequestException as e:
        return f"Erro de requisição: {str(e)}", thread_id
    except KeyError:
        return "Erro: Código do assistente inválido.", thread_id
    except Exception as e:
        return f"Erro inesperado: {str(e)}", thread_id


'''
async def transcrever_audio_whisper(id_contrato, caminho_arquivo):
    try:
        api_key, assistant_id = await get_credentials(id_contrato)

        client = OpenAI(api_key=api_key)

        with open(caminho_arquivo, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        print("Tipo da resposta da transcrição:", type(transcription))

        if isinstance(transcription, dict):
            return transcription.get('text', 'Texto não encontrado na resposta')

        elif isinstance(transcription, str):
            return transcription

        return {'Erro': 'Resposta da transcrição em formato inesperado'}

    except Exception as e:
        return {'Erro': f"Erro inesperado: {str(e)}"}
'''


