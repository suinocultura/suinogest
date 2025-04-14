"""
Utilitário para sincronização do aplicativo offline com o Firebase Cloud Firestore
"""
import os
import json
import sqlite3
from datetime import datetime
import requests

class FirebaseSync:
    """
    Classe para sincronizar dados entre o SQLite local e o Firebase Firestore
    """
    def __init__(self, db_path="suinocultura.db", api_url=None):
        """
        Inicializa a classe de sincronização
        
        Args:
            db_path (str): Caminho para o banco de dados SQLite
            api_url (str): URL da API de sincronização (Streamlit Cloud ou Firebase Functions)
        """
        self.db_path = db_path
        self.api_url = api_url
        self.sync_folder = "sync_data"
        
        # Criar pasta para os dados de sincronização se não existir
        if not os.path.exists(self.sync_folder):
            os.makedirs(self.sync_folder)
    
    def export_data_for_sync(self, user_id=None):
        """
        Exporta todos os dados do banco de dados para um arquivo JSON para sincronização
        
        Args:
            user_id (str): ID do usuário para associar aos dados exportados
        
        Returns:
            str: Caminho do arquivo JSON exportado ou None em caso de erro
        """
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obter todas as tabelas do banco de dados
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            
            # Exportar dados de cada tabela
            export_data = {}
            
            for table in tables:
                # Pular tabelas do sistema SQLite
                if table.startswith('sqlite_'):
                    continue
                
                # Consultar todos os dados da tabela
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Converter para lista de dicionários
                table_data = []
                for row in rows:
                    row_dict = dict(row)
                    # Garantir que o ID seja uma string (padrão do Firestore)
                    if 'id' in row_dict:
                        row_dict['id'] = str(row_dict['id'])
                    table_data.append(row_dict)
                
                export_data[table] = table_data
            
            # Adicionar metadados
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            export_data['timestamp'] = timestamp
            export_data['versao_app'] = "1.0.0"
            if user_id:
                export_data['user_id'] = user_id
            
            # Gerar nome do arquivo com timestamp
            filename = f"{self.sync_folder}/sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Salvar em arquivo JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            # Fechar conexão
            conn.close()
            
            return filename
        
        except Exception as e:
            print(f"Erro ao exportar dados para sincronização: {e}")
            return None
    
    def import_data_from_sync(self, json_file):
        """
        Importa dados de um arquivo JSON de sincronização para o banco de dados local
        
        Args:
            json_file (str): Caminho do arquivo JSON
        
        Returns:
            bool: True se importado com sucesso, False caso contrário
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(json_file):
                print(f"Arquivo não encontrado: {json_file}")
                return False
            
            # Carregar dados do arquivo JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Conectar ao banco de dados
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Processar cada tabela
            for table, rows in import_data.items():
                # Pular metadados que não são tabelas
                if table in ['timestamp', 'versao_app', 'user_id']:
                    continue
                
                # Verificar se a tabela existe
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not cursor.fetchone():
                    print(f"Tabela não encontrada no banco de dados: {table}")
                    continue
                
                # Processar cada linha
                for row in rows:
                    # Obter colunas da tabela
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Filtrar apenas as colunas existentes
                    filtered_row = {k: v for k, v in row.items() if k in columns}
                    
                    # Verificar se o registro já existe pelo ID
                    if 'id' in filtered_row:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE id = ?", (filtered_row['id'],))
                        exists = cursor.fetchone()[0] > 0
                        
                        if exists:
                            # Atualizar registro existente
                            set_clause = ', '.join([f"{k} = ?" for k in filtered_row.keys() if k != 'id'])
                            values = [filtered_row[k] for k in filtered_row.keys() if k != 'id'] + [filtered_row['id']]
                            
                            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
                        else:
                            # Inserir novo registro
                            columns_str = ', '.join(filtered_row.keys())
                            placeholders = ', '.join(['?' for _ in filtered_row.keys()])
                            values = list(filtered_row.values())
                            
                            cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
                    else:
                        # Sem ID, apenas inserir
                        columns_str = ', '.join(filtered_row.keys())
                        placeholders = ', '.join(['?' for _ in filtered_row.keys()])
                        values = list(filtered_row.values())
                        
                        cursor.execute(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})", values)
            
            # Commit e fechar conexão
            conn.commit()
            conn.close()
            
            return True
        
        except Exception as e:
            print(f"Erro ao importar dados: {e}")
            return False
    
    def send_data_to_api(self, json_file, user_id=None):
        """
        Envia dados para uma API de sincronização (Streamlit Cloud ou Firebase Functions)
        
        Args:
            json_file (str): Caminho do arquivo JSON
            user_id (str): ID do usuário para autenticação
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        if not self.api_url:
            print("URL da API não configurada")
            return False
        
        try:
            # Carregar dados do arquivo JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            # Adicionar ID do usuário se fornecido
            if user_id and 'user_id' not in sync_data:
                sync_data['user_id'] = user_id
            
            # Enviar dados para a API
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.api_url, json=sync_data, headers=headers)
            
            # Verificar resposta
            if response.status_code == 200:
                print("Dados enviados com sucesso!")
                return True
            else:
                print(f"Erro ao enviar dados: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"Erro ao enviar dados para API: {e}")
            return False


# Função auxiliar para obter uma instância da classe
def get_sync_manager(db_path="suinocultura.db", api_url=None):
    """
    Obtém uma instância do gerenciador de sincronização
    
    Args:
        db_path (str): Caminho para o banco de dados SQLite
        api_url (str): URL da API de sincronização
    
    Returns:
        FirebaseSync: Instância do gerenciador de sincronização
    """
    return FirebaseSync(db_path, api_url)