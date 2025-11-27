import os
import msal
import requests
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """
    Obtém token de acesso via MSAL (Client Credentials Flow).
    """
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        raise ValueError("Credenciais do Azure (TENANT_ID, CLIENT_ID, CLIENT_SECRET) não configuradas.")

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )

    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in result:
        return result["access_token"]
    else:
        error_desc = result.get("error_description", "Erro desconhecido")
        raise Exception(f"Falha na autenticação MSAL: {error_desc}")

def upload_file(file_path, remote_name, token):
    """
    Faz upload de um arquivo para o SharePoint via Graph API.
    """
    site_id = os.getenv("SP_SITE_ID")
    drive_id = os.getenv("SP_DRIVE_ID")
    folder_path = os.getenv("SP_FOLDER_PATH", "") # Opcional

    if not all([site_id, drive_id]):
        raise ValueError("IDs do SharePoint (SP_SITE_ID, SP_DRIVE_ID) não configurados.")

    # Construir caminho remoto
    if folder_path:
        # Garantir que não comece com / mas termine sem / se não for vazio
        folder_clean = folder_path.strip("/")
        remote_path = f"{folder_clean}/{remote_name}"
    else:
        remote_path = remote_name

    # Endpoint para upload (PUT content)
    # https://graph.microsoft.com/v1.0/sites/{site-id}/drives/{drive-id}/root:/{item-path}:/content
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{remote_path}:/content"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/csv" # Ou application/octet-stream
    }

    print(f"Iniciando upload de {remote_name} para {remote_path}...")
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        response = requests.put(url, headers=headers, data=file_content)
        
        if response.status_code in (200, 201):
            print(f"Sucesso: {remote_name} enviado.")
        else:
            print(f"Erro no upload de {remote_name}: {response.status_code} - {response.text}")
            response.raise_for_status()
            
    except FileNotFoundError:
        print(f"Arquivo local não encontrado: {file_path}")
    except Exception as e:
        print(f"Falha ao enviar {remote_name}: {e}")
        raise

def upload_csvs_to_sharepoint(local_dir: str) -> None:
    """
    Lê os arquivos CSV do diretório local_dir e faz upload para o SharePoint.
    """
    files_to_upload = [
        "dtic_tickets_detalhe.csv",
        "dtic_metricas_mensais.csv",
        "dtic_rankings.csv"
    ]

    try:
        print("Obtendo token de acesso do Azure...")
        token = get_access_token()
        
        for filename in files_to_upload:
            local_path = os.path.join(local_dir, filename)
            if os.path.exists(local_path):
                upload_file(local_path, filename, token)
            else:
                print(f"Aviso: Arquivo {filename} não encontrado em {local_dir}. Pulando.")
                
    except Exception as e:
        print(f"Erro crítico no processo de upload: {e}")

if __name__ == "__main__":
    # Teste (requer .env configurado)
    upload_csvs_to_sharepoint("output")
