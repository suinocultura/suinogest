"""
Serviço para integração do Firebase Firestore com o Sistema Suinocultura
"""
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import streamlit as st
import os

class FirestoreService:
    """
    Classe para gerenciar operações com o Firebase Firestore
    Permite sincronizar dados entre o aplicativo offline e o Streamlit Cloud
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementação de singleton para garantir uma única instância da classe"""
        if cls._instance is None:
            cls._instance = super(FirestoreService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa a conexão com o Firestore"""
        if not FirestoreService._initialized:
            self.db = None
            self.app = None
            self.initialize_app()
            FirestoreService._initialized = True
    
    def initialize_app(self):
        """Inicializa o aplicativo Firebase se ainda não estiver inicializado"""
        if self.app is not None:
            return
        
        try:
            # Verificar se já existe um app inicializado
            self.app = firebase_admin.get_app()
        except ValueError:
            # Nenhum app inicializado, criar um novo
            try:
                # Tentar obter credenciais de variáveis de ambiente ou secrets.toml
                cred_json = None
                
                # Verificar se existe um arquivo de credenciais no disco
                if os.path.exists('firebase-credentials.json'):
                    with open('firebase-credentials.json', 'r') as f:
                        cred_json = json.load(f)
                
                # Se não encontrou no disco, tentar obter das secrets do Streamlit
                if cred_json is None:
                    try:
                        cred_json = st.secrets["firebase"]
                    except:
                        st.warning("Credenciais do Firebase não encontradas em secrets.toml")
                
                # Se ainda não encontrou, buscar de variáveis de ambiente
                if cred_json is None:
                    firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
                    if firebase_creds:
                        cred_json = json.loads(firebase_creds)
                
                # Se encontrou as credenciais, inicializar o app
                if cred_json:
                    cred = credentials.Certificate(cred_json)
                    self.app = firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                else:
                    st.error("Não foi possível encontrar as credenciais do Firebase")
            except Exception as e:
                st.error(f"Erro ao inicializar o Firebase: {str(e)}")
        
        # Se o app já estava inicializado, obter o cliente Firestore
        if self.app and not self.db:
            self.db = firestore.client()
    
    def get_collection(self, collection_name):
        """
        Obtém uma referência para uma coleção
        
        Args:
            collection_name (str): Nome da coleção
        
        Returns:
            CollectionReference: Referência para a coleção
        """
        if not self.db:
            self.initialize_app()
        
        if self.db:
            return self.db.collection(collection_name)
        
        return None
    
    def get_document(self, collection_name, document_id):
        """
        Obtém um documento específico
        
        Args:
            collection_name (str): Nome da coleção
            document_id (str): ID do documento
        
        Returns:
            dict: Dados do documento ou None se não encontrado
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return None
        
        try:
            doc_ref = collection.document(document_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            
            return None
        except Exception as e:
            print(f"Erro ao obter documento: {str(e)}")
            return None
    
    def save_document(self, collection_name, document_id, data):
        """
        Salva um documento no Firestore
        
        Args:
            collection_name (str): Nome da coleção
            document_id (str): ID do documento
            data (dict): Dados a serem salvos
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        try:
            # Adicionar timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Salvar documento
            doc_ref = collection.document(document_id)
            doc_ref.set(data)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar documento: {str(e)}")
            return False
    
    def update_document(self, collection_name, document_id, data):
        """
        Atualiza um documento existente
        
        Args:
            collection_name (str): Nome da coleção
            document_id (str): ID do documento
            data (dict): Dados a serem atualizados
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        try:
            # Adicionar timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Atualizar documento
            doc_ref = collection.document(document_id)
            doc_ref.update(data)
            
            return True
        except Exception as e:
            print(f"Erro ao atualizar documento: {str(e)}")
            return False
    
    def delete_document(self, collection_name, document_id):
        """
        Exclui um documento
        
        Args:
            collection_name (str): Nome da coleção
            document_id (str): ID do documento
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return False
        
        try:
            # Excluir documento
            doc_ref = collection.document(document_id)
            doc_ref.delete()
            
            return True
        except Exception as e:
            print(f"Erro ao excluir documento: {str(e)}")
            return False
    
    def query_collection(self, collection_name, filters=None, order_by=None, limit=None):
        """
        Consulta documentos em uma coleção com filtros opcionais
        
        Args:
            collection_name (str): Nome da coleção
            filters (list): Lista de tuplas (campo, operador, valor)
            order_by (tuple): (campo, direção) para ordenação
            limit (int): Limite de documentos a retornar
        
        Returns:
            list: Lista de documentos encontrados
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return []
        
        try:
            query = collection
            
            # Aplicar filtros
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            # Aplicar ordenação
            if order_by:
                field, direction = order_by
                if direction.lower() == 'desc':
                    query = query.order_by(field, direction=firestore.Query.DESCENDING)
                else:
                    query = query.order_by(field)
            
            # Aplicar limite
            if limit:
                query = query.limit(limit)
            
            # Executar consulta
            docs = query.stream()
            
            # Converter para lista de dicionários
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
        except Exception as e:
            print(f"Erro ao consultar coleção: {str(e)}")
            return []
    
    def batch_save(self, collection_name, documents):
        """
        Salva vários documentos em lote
        
        Args:
            collection_name (str): Nome da coleção
            documents (list): Lista de tuplas (document_id, data)
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not self.db:
            self.initialize_app()
            
        if not self.db:
            return False
        
        try:
            # Criar batch
            batch = self.db.batch()
            
            # Adicionar operações ao batch
            collection_ref = self.db.collection(collection_name)
            for doc_id, data in documents:
                # Adicionar timestamp
                data['updated_at'] = firestore.SERVER_TIMESTAMP
                
                # Adicionar ao batch
                doc_ref = collection_ref.document(doc_id)
                batch.set(doc_ref, data)
            
            # Commit do batch
            batch.commit()
            
            return True
        except Exception as e:
            print(f"Erro ao salvar documentos em lote: {str(e)}")
            return False
    
    def import_from_json(self, json_data, collection_prefix=""):
        """
        Importa dados de um JSON para o Firestore
        
        Args:
            json_data (dict): Dados JSON a serem importados
            collection_prefix (str): Prefixo para as coleções
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not self.db:
            self.initialize_app()
            
        if not self.db:
            return False
        
        try:
            # Criar batch
            batch = self.db.batch()
            success = True
            
            # Processar cada coleção
            for collection_name, items in json_data.items():
                # Pular metadados que não são coleções
                if collection_name in ['timestamp', 'versao_app', 'user_id']:
                    continue
                
                # Nome da coleção com prefixo
                full_collection_name = f"{collection_prefix}_{collection_name}" if collection_prefix else collection_name
                collection_ref = self.db.collection(full_collection_name)
                
                # Processar cada documento
                for item in items:
                    # Garantir que existe um ID
                    doc_id = str(item.get('id', datetime.now().strftime("%Y%m%d%H%M%S")))
                    
                    # Referência ao documento
                    doc_ref = collection_ref.document(doc_id)
                    
                    # Adicionar timestamp
                    item['updated_at'] = firestore.SERVER_TIMESTAMP
                    
                    # Adicionar ao batch
                    batch.set(doc_ref, item)
                    
                    # Se o batch ficar muito grande, commit e criar um novo
                    if len(batch._writes) >= 400:  # Limite de operações por batch
                        batch.commit()
                        batch = self.db.batch()
            
            # Commit final
            if len(batch._writes) > 0:
                batch.commit()
            
            return success
        except Exception as e:
            print(f"Erro ao importar dados: {str(e)}")
            return False
    
    def export_to_json(self, collections, output_file=None):
        """
        Exporta dados do Firestore para JSON
        
        Args:
            collections (list): Lista de nomes de coleções para exportar
            output_file (str): Caminho do arquivo de saída
        
        Returns:
            dict: Dados JSON exportados
        """
        result = {}
        
        try:
            # Exportar cada coleção
            for collection_name in collections:
                collection = self.get_collection(collection_name)
                if not collection:
                    continue
                
                # Obter todos os documentos
                docs = collection.stream()
                
                # Converter para lista de dicionários
                collection_data = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    collection_data.append(data)
                
                result[collection_name] = collection_data
            
            # Adicionar metadados
            result['timestamp'] = datetime.now().isoformat()
            
            # Salvar em arquivo se especificado
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            return result
        except Exception as e:
            print(f"Erro ao exportar dados: {str(e)}")
            return {'error': str(e)}
    
    def sync_offline_data(self, json_data, user_id):
        """
        Sincroniza dados do aplicativo offline com o Firestore
        
        Args:
            json_data (dict): Dados exportados do aplicativo offline
            user_id (str): ID do usuário para associar aos dados
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        if not json_data:
            return False
        
        # Adicionar prefixo de usuário para isolamento de dados
        collection_prefix = f"user_{user_id}"
        
        # Importar dados para o Firestore
        return self.import_from_json(json_data, collection_prefix)

# Função auxiliar para obter a instância do serviço Firestore
def get_firestore_service():
    """
    Função auxiliar para obter a instância do serviço Firestore
    
    Returns:
        FirestoreService: Instância do serviço Firestore
    """
    return FirestoreService()