"""
API para sincronização de dados entre o aplicativo offline e o Streamlit Cloud
Este arquivo implementa endpoints para importar e exportar dados do Firebase Firestore
"""
import streamlit as st
from firestore_service import get_firestore_service
import json
import time
from datetime import datetime

# Configurar cabeçalhos CORS para permitir acesso de origens externas
def add_cors_headers():
    """
    Adiciona cabeçalhos CORS para permitir acesso de origens externas
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return headers

def validate_auth(request):
    """
    Valida a autenticação da requisição
    
    Args:
        request: Objeto de requisição
    
    Returns:
        tuple: (success, user_id ou mensagem de erro)
    """
    # Verificar token de API
    if "X-API-KEY" in request.headers:
        api_key = request.headers["X-API-KEY"]
        
        # Em produção, usar secrets.toml para armazenar e verificar as chaves
        valid_keys = []
        
        try:
            valid_keys = st.secrets.get("api_keys", [])
        except:
            # Fallback para ambiente de desenvolvimento
            valid_keys = ["test_api_key_123"]
        
        if api_key in valid_keys:
            # Extrair user_id do corpo da requisição
            try:
                data = json.loads(request.body)
                user_id = data.get("user_id")
                if user_id:
                    return True, user_id
                return False, "User ID não fornecido"
            except:
                return False, "Corpo da requisição inválido"
        
        return False, "Chave API inválida"
    
    return False, "Autenticação necessária"

def sync_handler():
    """
    Manipulador para o endpoint de sincronização
    """
    # Obter o serviço Firestore
    firestore = get_firestore_service()
    
    # Verificar método da requisição
    request = st._get_request()
    if request.method == "OPTIONS":
        # Responder à solicitação de preflight CORS
        return {"headers": add_cors_headers()}
    
    elif request.method == "POST":
        # Validar autenticação
        auth_success, auth_result = validate_auth(request)
        if not auth_success:
            return {
                "status_code": 401,
                "body": json.dumps({"error": auth_result}),
                "headers": add_cors_headers(),
            }
        
        user_id = auth_result
        
        # Processar dados de sincronização
        try:
            # Analisar o corpo da requisição JSON
            data = json.loads(request.body)
            
            # Sincronizar com o Firestore
            sync_success = firestore.sync_offline_data(data, user_id)
            
            if sync_success:
                return {
                    "status_code": 200,
                    "body": json.dumps({
                        "success": True,
                        "message": "Dados sincronizados com sucesso",
                        "timestamp": datetime.now().isoformat()
                    }),
                    "headers": add_cors_headers(),
                }
            else:
                return {
                    "status_code": 500,
                    "body": json.dumps({"error": "Erro ao sincronizar dados"}),
                    "headers": add_cors_headers(),
                }
        
        except Exception as e:
            return {
                "status_code": 400,
                "body": json.dumps({"error": f"Erro ao processar requisição: {str(e)}"}),
                "headers": add_cors_headers(),
            }
    
    else:
        # Método não permitido
        return {
            "status_code": 405,
            "body": json.dumps({"error": "Método não permitido"}),
            "headers": add_cors_headers(),
        }

def export_handler():
    """
    Manipulador para o endpoint de exportação
    """
    # Obter o serviço Firestore
    firestore = get_firestore_service()
    
    # Verificar método da requisição
    request = st._get_request()
    if request.method == "OPTIONS":
        # Responder à solicitação de preflight CORS
        return {"headers": add_cors_headers()}
    
    elif request.method == "GET":
        # Validar autenticação
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {
                "status_code": 401,
                "body": json.dumps({"error": "Token de autenticação não fornecido"}),
                "headers": add_cors_headers(),
            }
        
        token = auth_header.split("Bearer ")[1].strip()
        
        # Em produção, verificar o token
        # Aqui estamos apenas verificando se não está vazio
        if not token:
            return {
                "status_code": 401,
                "body": json.dumps({"error": "Token inválido"}),
                "headers": add_cors_headers(),
            }
        
        # Obter parâmetros
        user_id = request.query_params.get("user_id")
        collections = request.query_params.get("collections", "").split(",")
        
        if not user_id:
            return {
                "status_code": 400,
                "body": json.dumps({"error": "User ID não fornecido"}),
                "headers": add_cors_headers(),
            }
        
        if not collections or collections == [""]:
            # Usar coleções padrão se não especificado
            collections = ["usuarios", "animais", "saude", "reproducao", "crescimento"]
        
        # Adicionar prefixo de usuário às coleções
        prefixed_collections = [f"user_{user_id}_{col}" for col in collections]
        
        try:
            # Exportar dados do Firestore
            export_data = firestore.export_to_json(prefixed_collections)
            
            # Remover o prefixo das coleções para o resultado
            result = {}
            for col, data in export_data.items():
                if col.startswith(f"user_{user_id}_"):
                    # Remover o prefixo
                    original_col = col[len(f"user_{user_id}_"):]
                    result[original_col] = data
                else:
                    result[col] = data
            
            # Adicionar metadados
            result["timestamp"] = datetime.now().isoformat()
            result["user_id"] = user_id
            
            return {
                "status_code": 200,
                "body": json.dumps(result),
                "headers": add_cors_headers(),
            }
        
        except Exception as e:
            return {
                "status_code": 500,
                "body": json.dumps({"error": f"Erro ao exportar dados: {str(e)}"}),
                "headers": add_cors_headers(),
            }
    
    else:
        # Método não permitido
        return {
            "status_code": 405,
            "body": json.dumps({"error": "Método não permitido"}),
            "headers": add_cors_headers(),
        }

# Mapear endpoints para manipuladores
endpoints = {
    "/api/sync": sync_handler,
    "/api/export": export_handler,
}

# Função principal que será chamada pelo Streamlit
def api_dispatcher():
    # Obter o caminho da URL atual
    request = st._get_request()
    path = request.path
    
    # Verificar se o caminho corresponde a um endpoint da API
    handler = endpoints.get(path)
    if handler:
        return handler()
    
    # Endpoint não encontrado
    return {
        "status_code": 404,
        "body": json.dumps({"error": "Endpoint não encontrado"}),
        "headers": add_cors_headers(),
    }

# Adicionar o manipulador ao Streamlit
st.experimental_set_query_params(
    _stcore_api_handler=api_dispatcher
)