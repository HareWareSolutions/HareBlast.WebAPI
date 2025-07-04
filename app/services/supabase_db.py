import base64
import io
from typing import Optional, Dict, Any
from supabase import create_client, Client

SUPABASE_URL = "https://ucfgqlccobtvinarypts.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVjZmdxbGNjb2J0dmluYXJ5cHRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NDgxNTUsImV4cCI6MjA2NzEyNDE1NX0.QN7qfwXR9f7rZ_ydTMt07KwrdcxoRBfLEBs_VZ9XjoQ"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def upload_base64_image(
    base64_string: str,
    file_name: str,
    bucket_name: str = "public",
    storage_path: Optional[str] = None,
    content_type: str = "image/jpeg",
    overwrite: bool = False
) -> Dict[str, Any]:

    if "," in base64_string:
        base64_string = base64_string.split(",", 1)[1]

    try:
        image_data = base64.b64decode(base64_string)

        full_path = f"{storage_path.strip('/') + '/' if storage_path else ''}{file_name}"

        storage = supabase.storage.from_(bucket_name)
        if overwrite:
            response = storage.update(
                path=full_path,
                file=image_data,
                file_options={"content_type": content_type}
            )
        else:
            response = storage.upload(
                path=full_path,
                file=image_data,
                file_options={"content_type": content_type}
            )

        if hasattr(response, 'error') and response.error:
            return {
                "status": "error",
                "message": response.error.message
            }

        public_url = storage.get_public_url(full_path)

        return {
            "status": "success",
            "path": full_path,
            "public_url": public_url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def folder_exists(bucket_name: str, folder_path: str):
    try:
        result = supabase.storage.from_(bucket_name).list(path=folder_path)
        return len(result) > 0
    except Exception:
        return False


async def create_folder_if_not_exists(bucket_name: str, folder_path: str):
    try:
        response = create_folder_if_not_exists(bucket_name, folder_path)
        return True, response
    except Exception as e:
        return None


async def delete_file(bucket: str, caminhos: list[str]):
    try:
        response = await supabase.storage.from_(bucket).remove(caminhos)
        return response
    except Exception as e:
        return False, None


''''
def main():
    try:
        # Criar uma pasta simples
        result1 = create_folder(
            bucket_name="imagens",
            folder_path="usuarios/123/fotos"
        )
        print(f"Pasta 'usuarios/123/fotos' criada com sucesso!")

        # Criar uma estrutura de pastas aninhadas
        # Você precisa criar cada nível separadamente
        folders = [
            "projetos",
            "projetos/projeto1",
            "projetos/projeto1/documentos",
            "projetos/projeto1/imagens"
        ]

        for folder in folders:
            result = create_folder(bucket_name="arquivos", folder_path=folder)
            print(f"Pasta '{folder}' criada com sucesso!")

    except Exception as e:
        print(f"Erro ao criar pasta: {str(e)}")

'''