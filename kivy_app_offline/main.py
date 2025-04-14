import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.garden.iconfonts import register
from kivy.factory import Factory

# Importar bibliotecas para banco de dados SQLite
import sqlite3
import os
import json
from datetime import datetime, timedelta
import time
import random
import threading

# Definindo esquema de cores moderno do aplicativo
COR_PRIMARIA = "#6200EA"  # Roxo profundo - cor principal
COR_SECUNDARIA = "#3700B3"  # Roxo escuro - ações secundárias
COR_ACENTO = "#03DAC6"  # Verde água - destaques
COR_ERRO = "#CF6679"  # Rosa - erros e alertas
COR_FUNDO = "#121212"  # Cinza escuro - fundo do app
COR_SUPERFICIE = "#1E1E1E"  # Cinza um pouco mais claro - superfícies
COR_TEXTO_PRIMARIO = "#FFFFFF"  # Branco - texto principal
COR_TEXTO_SECUNDARIO = "#B0B0B0"  # Cinza claro - texto secundário

# Cores antigas para compatibilidade com código existente
ROXO_PRIMARIO = COR_PRIMARIA
ROXO_ESCURO = COR_SECUNDARIA
ROXO_CLARO = "#BB86FC"  # Roxo mais claro
CINZA_CLARO = "#2D2D2D"  # Cinza escuro para tema escuro
CINZA_ESCURO = "#D0D0D0"  # Texto cinza claro
BRANCO = COR_TEXTO_PRIMARIO

# Configurar a janela
Window.clearcolor = get_color_from_hex(COR_FUNDO)
Window.softinput_mode = 'below_target'  # Não desloca widgets quando o teclado aparece

# Configurar Window (para desenvolvimento)
Window.size = (360, 640)  # Simulando um telefone

# Classe para gerenciar o banco de dados
class DatabaseManager:
    def __init__(self, db_path="suinocultura.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.create_connection()
        self.setup_database()
    
    def create_connection(self):
        """Cria conexão com o banco de dados SQLite"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
            self.cursor = self.connection.cursor()
            print(f"Conexão estabelecida com {self.db_path}")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
    
    def setup_database(self):
        """Configura as tabelas do banco de dados se não existirem"""
        try:
            # Tabela de usuários (para login offline)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                cargo TEXT,
                senha TEXT,
                data_criacao TEXT
            )
            ''')
            
            # Tabela de animais
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                raca TEXT,
                nascimento TEXT,
                status TEXT DEFAULT 'Ativo',
                peso_nascimento REAL,
                data_cadastro TEXT,
                observacoes TEXT
            )
            ''')
            
            # Tabela de reprodução
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reproducao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_animal INTEGER,
                tipo_evento TEXT,
                data_evento TEXT,
                observacoes TEXT,
                FOREIGN KEY (id_animal) REFERENCES animais (id)
            )
            ''')
            
            # Tabela de saúde
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS saude (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_animal INTEGER,
                tipo_evento TEXT,
                data_evento TEXT,
                medicamento TEXT,
                dosagem TEXT,
                observacoes TEXT,
                FOREIGN KEY (id_animal) REFERENCES animais (id)
            )
            ''')
            
            # Tabela de crescimento
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS crescimento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_animal INTEGER,
                data_pesagem TEXT,
                peso REAL,
                altura REAL,
                observacoes TEXT,
                FOREIGN KEY (id_animal) REFERENCES animais (id)
            )
            ''')
            
            # Insere usuário admin padrão se não existir
            self.cursor.execute('''
            INSERT OR IGNORE INTO usuarios (matricula, nome, cargo, senha, data_criacao)
            VALUES (?, ?, ?, ?, ?)
            ''', ('123456', 'Administrador', 'Admin', '123456', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            self.connection.commit()
            print("Banco de dados configurado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao configurar o banco de dados: {e}")
    
    def query(self, sql, params=()):
        """Executa uma consulta SQL e retorna os resultados"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro na consulta: {e}")
            return []
    
    def execute(self, sql, params=()):
        """Executa um comando SQL e faz commit"""
        try:
            self.cursor.execute(sql, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao executar comando: {e}")
            return False
    
    def executemany(self, sql, params_list):
        """Executa vários comandos SQL e faz commit"""
        try:
            self.cursor.executemany(sql, params_list)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao executar múltiplos comandos: {e}")
            return False
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            print("Conexão com o banco de dados fechada")
    
    def __del__(self):
        """Destrutor para garantir que a conexão seja fechada"""
        self.close()

# Classe para autenticação e gerenciamento de usuários
class UserManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
    
    def authenticate(self, matricula, senha=None):
        """Autentica um usuário pelo número de matrícula"""
        users = self.db_manager.query(
            "SELECT * FROM usuarios WHERE matricula = ?",
            (matricula,)
        )
        
        if users:
            user = dict(users[0])
            # Para simplificar, não estamos verificando a senha neste exemplo
            # Em um app real, você deve implementar verificação segura de senha
            self.current_user = user
            return user
        
        return None
    
    def get_current_user(self):
        """Retorna o usuário atual"""
        return self.current_user
    
    def logout(self):
        """Faz logout do usuário atual"""
        self.current_user = None

# Classe de tela de login
class LoginScreen(Screen):
    def __init__(self, user_manager, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.user_manager = user_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Adicionar logo no topo
        logo_layout = BoxLayout(orientation='vertical', size_hint_y=0.3)
        logo = Image(source='kivy_app_offline/assets/logo_placeholder.png', 
                     size_hint=(None, None), size=(dp(150), dp(150)),
                     pos_hint={'center_x': 0.5, 'center_y': 0.5})
        logo_layout.add_widget(logo)
        
        # Título do app
        title = Label(text='Sistema Suinocultura', 
                      font_size=dp(24), 
                      color=get_color_from_hex(ROXO_PRIMARIO),
                      size_hint_y=None, height=dp(50))
        
        # Campos de login
        self.matricula_input = TextInput(
            hint_text='Matrícula', 
            multiline=False, 
            size_hint_y=None, height=dp(50),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Botão de login
        login_button = Button(
            text='Entrar', 
            size_hint_y=None, height=dp(50),
            background_normal='',
            background_color=get_color_from_hex(ROXO_PRIMARIO),
            color=get_color_from_hex(BRANCO)
        )
        login_button.bind(on_press=self.login)
        
        # Mensagem de status (inicialmente vazia)
        self.status_label = Label(
            text='', 
            color=get_color_from_hex('#FF5252'),
            size_hint_y=None, height=dp(30)
        )
        
        # Adicionar widgets ao layout
        layout.add_widget(logo_layout)
        layout.add_widget(title)
        layout.add_widget(self.matricula_input)
        layout.add_widget(login_button)
        layout.add_widget(self.status_label)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def login(self, instance):
        # Lógica de autenticação
        matricula = self.matricula_input.text.strip()
        
        if not matricula:
            self.status_label.text = "Por favor, informe sua matrícula"
            return
        
        # Autenticar usuário
        user = self.user_manager.authenticate(matricula)
        
        if user:
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'menu'
        else:
            self.status_label.text = "Matrícula não encontrada"

# Classe de tela de menu principal
class MenuScreen(Screen):
    def __init__(self, user_manager, db_manager, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.user_manager = user_manager
        self.db_manager = db_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # Barra superior
        topbar = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, height=dp(60),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Adicionar cor de fundo à barra superior
        with topbar.canvas.before:
            Color(*get_color_from_hex(ROXO_PRIMARIO))
            self.rect = Rectangle(pos=topbar.pos, size=topbar.size)
            topbar.bind(pos=self.update_rect, size=self.update_rect)
        
        # Título na barra superior
        title_label = Label(
            text='Sistema Suinocultura', 
            font_size=dp(18),
            color=get_color_from_hex(BRANCO)
        )
        
        # Botão de menu (simulado)
        menu_button = Button(
            text='≡', 
            font_size=dp(24),
            size_hint_x=None, width=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO),
            color=get_color_from_hex(BRANCO)
        )
        
        # Adicionar widgets à barra superior
        topbar.add_widget(menu_button)
        topbar.add_widget(title_label)
        
        # Área de conteúdo com scroll
        scroll_view = ScrollView()
        self.content_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(10), 
            padding=dp(10),
            size_hint_y=None
        )
        
        # Definir altura do conteúdo para permitir rolagem
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        # Lista de módulos disponíveis
        self.modulos = [
            {"nome": "Cadastro de Animais", "icone": "🐷", "tela": "animal"},
            {"nome": "Reprodução", "icone": "🔄", "tela": "reproducao"},
            {"nome": "Crescimento", "icone": "📈", "tela": "crescimento"},
            {"nome": "Saúde", "icone": "🏥", "tela": "saude"},
            {"nome": "Relatórios", "icone": "📊", "tela": "relatorios"},
            {"nome": "Exportar Dados", "icone": "📤", "tela": "exportar"},
            {"nome": "Importar Dados", "icone": "📥", "tela": "importar"},
            {"nome": "Sincronizar com Cloud", "icone": "☁️", "tela": "sincronizar"},
            {"nome": "Configurações", "icone": "⚙️", "tela": "configuracoes"},
            {"nome": "Logout", "icone": "🚪", "tela": "logout"}
        ]
        
        # Criar botões para cada módulo
        self.criar_botoes_menu()
        
        # Adicionar conteúdo ao ScrollView
        scroll_view.add_widget(self.content_layout)
        
        # Adicionar widgets ao layout principal
        layout.add_widget(topbar)
        layout.add_widget(scroll_view)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        """Atualizar posição do retângulo de fundo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def criar_botoes_menu(self):
        """Criar botões para cada módulo"""
        self.content_layout.clear_widgets()
        
        # Mostrar informações do usuário
        user = self.user_manager.get_current_user()
        if user:
            # Caixa de informações do usuário
            user_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None, height=dp(80),
                padding=dp(10)
            )
            
            # Adicionar fundo à caixa de usuário
            with user_box.canvas.before:
                Color(*get_color_from_hex(ROXO_CLARO))
                RoundedRectangle(pos=user_box.pos, size=user_box.size, radius=[dp(5)])
                user_box.bind(pos=self.update_user_box, size=self.update_user_box)
            
            # Nome do usuário
            lbl_nome = Label(
                text=f"Olá, {user['nome']}",
                font_size=dp(18),
                color=get_color_from_hex(ROXO_ESCURO),
                bold=True,
                size_hint_y=None, height=dp(30),
                halign='left',
                text_size=(Window.width - dp(40), None)
            )
            
            # Cargo do usuário
            lbl_cargo = Label(
                text=f"Cargo: {user['cargo']}",
                font_size=dp(14),
                color=get_color_from_hex(CINZA_ESCURO),
                size_hint_y=None, height=dp(20),
                halign='left',
                text_size=(Window.width - dp(40), None)
            )
            
            user_box.add_widget(lbl_nome)
            user_box.add_widget(lbl_cargo)
            self.content_layout.add_widget(user_box)
            
            # Adicionar um espaçador
            spacer = BoxLayout(size_hint_y=None, height=dp(10))
            self.content_layout.add_widget(spacer)
        
        # Criar botões para cada módulo
        for modulo in self.modulos:
            btn = Button(
                text=f"{modulo['icone']} {modulo['nome']}",
                size_hint_y=None, height=dp(60),
                background_normal='',
                background_color=get_color_from_hex(CINZA_CLARO),
                color=get_color_from_hex(CINZA_ESCURO),
                halign='left',
                valign='middle',
                text_size=(Window.width - dp(40), dp(60)),
                padding_x=dp(20)
            )
            
            # Definir ação do botão
            if modulo['tela'] == 'logout':
                btn.bind(on_press=self.logout)
            elif modulo['tela'] == 'exportar':
                btn.bind(on_press=self.exportar_dados)
            elif modulo['tela'] == 'importar':
                btn.bind(on_press=self.importar_dados)
            elif modulo['tela'] == 'sincronizar':
                btn.bind(on_press=self.sincronizar_dados)
            else:
                btn.bind(on_press=lambda x, m=modulo: self.abrir_modulo(m))
            
            self.content_layout.add_widget(btn)
    
    def update_user_box(self, instance, value):
        """Atualizar retângulo da caixa de usuário"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*get_color_from_hex(ROXO_CLARO))
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(5)])
    
    def logout(self, instance):
        """Fazer logout e voltar para a tela de login"""
        self.user_manager.logout()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'
    
    def abrir_modulo(self, modulo):
        """Abrir o módulo selecionado"""
        if modulo['tela'] == 'animal':
            # Navegamos para a tela de animais
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'animal'
        elif modulo['tela'] == 'saude':
            # Navegamos para a tela de saúde
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'saude'
        elif modulo['tela'] == 'reproducao':
            # Navegamos para a tela de reprodução
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'reproducao'
        elif modulo['tela'] == 'crescimento':
            # Navegamos para a tela de crescimento
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'crescimento'
        else:
            # Para os outros módulos, mostramos um popup
            popup = Popup(
                title=f'Módulo: {modulo["nome"]}',
                content=Label(text=f'O módulo {modulo["nome"]} está em desenvolvimento.'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def exportar_dados(self, instance):
        """Exportar dados do banco de dados para JSON"""
        try:
            # Criar diretório para exportação se não existir
            export_dir = "dados_exportados"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Data atual para o nome do arquivo
            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = os.path.join(export_dir, f"suinocultura_export_{data_atual}.json")
            
            # Dados a serem exportados
            export_data = {
                "animais": [dict(row) for row in self.db_manager.query("SELECT * FROM animais")],
                "reproducao": [dict(row) for row in self.db_manager.query("SELECT * FROM reproducao")],
                "saude": [dict(row) for row in self.db_manager.query("SELECT * FROM saude")],
                "crescimento": [dict(row) for row in self.db_manager.query("SELECT * FROM crescimento")],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "versao_app": "1.0.0"
            }
            
            # Salvar em arquivo JSON
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=4)
            
            # Mostrar mensagem de sucesso
            popup = Popup(
                title='Sucesso',
                content=Label(text=f'Dados exportados com sucesso para:\n{export_file}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            
        except Exception as e:
            # Mostrar erro
            popup = Popup(
                title='Erro na Exportação',
                content=Label(text=f'Erro ao exportar dados: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def importar_dados(self, instance):
        """Importar dados de JSON para o banco de dados"""
        # Aqui seria implementada a lógica para selecionar um arquivo
        # Como isso é mais complexo no Kivy, estamos usando um popup informativo
        popup = Popup(
            title='Importação de Dados',
            content=Label(text='Para importar dados, coloque o arquivo JSON na pasta "dados_exportados" e reinicie o aplicativo.'),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        
    def sincronizar_dados(self, instance):
        """Sincroniza dados com o Firestore via API"""
        try:
            # Importar o gerenciador de sincronização
            from firebase_sync import get_sync_manager
            
            # Obter o usuário atual para associar aos dados
            user = self.user_manager.get_current_user()
            if not user:
                popup = Popup(
                    title='Erro',
                    content=Label(text='Você precisa estar logado para sincronizar dados.'),
                    size_hint=(0.8, 0.4)
                )
                popup.open()
                return
            
            # Obter ID do usuário
            user_id = str(user.get('id', '0'))
            
            # URL da API (ajustar conforme a implantação)
            api_url = "https://suinocultura-app.streamlit.app/api/sync"
            
            # Criar o gerenciador de sincronização
            sync_manager = get_sync_manager(self.db_manager.db_path, api_url)
            
            # Mostrar popup de processamento
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            content.add_widget(Label(text='Preparando dados para sincronização...'))
            progress = Label(text='0%')
            content.add_widget(progress)
            
            popup = Popup(
                title='Sincronizando',
                content=content,
                size_hint=(0.8, 0.4),
                auto_dismiss=False
            )
            popup.open()
            
            # Atualizar o progresso
            progress.text = "25% - Exportando dados..."
            
            # Exportar os dados
            export_file = sync_manager.export_data_for_sync(user_id)
            if not export_file:
                popup.dismiss()
                error_popup = Popup(
                    title='Erro',
                    content=Label(text='Falha ao exportar dados para sincronização.'),
                    size_hint=(0.8, 0.4)
                )
                error_popup.open()
                return
            
            # Atualizar o progresso
            progress.text = "50% - Enviando para o servidor..."
            
            # Se houver conexão com a internet, tentar enviar para o servidor
            try:
                import requests
                # Verificar conexão com a internet com timeout curto
                response = requests.get("https://www.google.com", timeout=3)
                online = response.status_code == 200
            except:
                online = False
            
            if online:
                # Enviar para o servidor
                success = sync_manager.send_data_to_api(export_file, user_id)
                if success:
                    progress.text = "100% - Sincronização concluída!"
                    popup.dismiss()
                    success_popup = Popup(
                        title='Sucesso',
                        content=Label(text='Dados sincronizados com sucesso!'),
                        size_hint=(0.8, 0.4)
                    )
                    success_popup.open()
                else:
                    progress.text = "75% - Salvando localmente..."
                    popup.dismiss()
                    warning_popup = Popup(
                        title='Aviso',
                        content=Label(text='Não foi possível enviar os dados para o servidor.\nDados salvos localmente para sincronização futura.'),
                        size_hint=(0.8, 0.4)
                    )
                    warning_popup.open()
            else:
                # Sem conexão, salvar localmente
                progress.text = "75% - Salvando localmente para sincronização futura..."
                popup.dismiss()
                offline_popup = Popup(
                    title='Offline',
                    content=Label(text='Sem conexão com a internet.\nDados salvos localmente para sincronização futura.'),
                    size_hint=(0.8, 0.4)
                )
                offline_popup.open()
            
        except Exception as e:
            # Mostrar erro
            popup = Popup(
                title='Erro na Sincronização',
                content=Label(text=f'Erro ao sincronizar dados: {str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()

# Classe para widget de Spinner personalizado
class SpinnerWidget(Button):
    dropdown = ObjectProperty(None)
    values = ListProperty([])
    
    def __init__(self, **kwargs):
        self.values = kwargs.pop('values', [])
        super(SpinnerWidget, self).__init__(**kwargs)
        self.bind(on_release=self.show_dropdown)
    
    def show_dropdown(self, *args):
        from kivy.uix.dropdown import DropDown
        
        # Criar dropdown
        self.dropdown = DropDown()
        
        # Adicionar botões para cada valor
        for value in self.values:
            btn = Button(
                text=value,
                size_hint_y=None,
                height=dp(44),
                background_normal='',
                background_color=get_color_from_hex(CINZA_CLARO),
                color=get_color_from_hex(CINZA_ESCURO)
            )
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        
        # Abrir dropdown
        self.dropdown.open(self)
        
        # Configurar o que acontece ao selecionar um valor
        self.dropdown.bind(on_select=lambda instance, x: setattr(self, 'text', x))

# Classe para a tela de cadastro de animais
class AnimalScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super(AnimalScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # Barra superior
        topbar = BoxLayout(orientation='horizontal', 
                          size_hint_y=None, height=dp(60),
                          padding=[dp(10), dp(10), dp(10), dp(10)])
        
        # Adicionar cor de fundo à barra superior
        topbar.canvas.before.clear()
        with topbar.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex(ROXO_PRIMARIO))
            self.rect = Rectangle(pos=topbar.pos, size=topbar.size)
            topbar.bind(pos=self.update_rect, size=self.update_rect)
        
        # Botão voltar
        back_button = Button(text='←', 
                           font_size=dp(24),
                           size_hint_x=None, width=dp(50),
                           background_color=get_color_from_hex(ROXO_PRIMARIO))
        back_button.bind(on_press=self.voltar_menu)
        
        # Título na barra superior
        title_label = Label(text='Cadastro de Animais', 
                           font_size=dp(18),
                           color=get_color_from_hex(BRANCO))
        
        # Adicionar widgets à barra superior
        topbar.add_widget(back_button)
        topbar.add_widget(title_label)
        
        # Abas para diferentes funções
        tabs_layout = BoxLayout(orientation='horizontal', 
                               size_hint_y=None, height=dp(50))
        
        # Botões das abas
        btn_listar = Button(text='Listar', 
                          background_color=get_color_from_hex(ROXO_ESCURO),
                          color=get_color_from_hex(BRANCO))
        btn_listar.bind(on_press=lambda x: self.mudar_aba('listar'))
        
        btn_cadastrar = Button(text='Cadastrar', 
                             background_color=get_color_from_hex(ROXO_CLARO),
                             color=get_color_from_hex(CINZA_ESCURO))
        btn_cadastrar.bind(on_press=lambda x: self.mudar_aba('cadastrar'))
        
        # Adicionar botões ao layout das abas
        tabs_layout.add_widget(btn_listar)
        tabs_layout.add_widget(btn_cadastrar)
        
        # Área de conteúdo
        self.content_area = BoxLayout(orientation='vertical')
        
        # Inicialmente mostrar lista de animais
        self.mostrar_lista_animais()
        
        # Adicionar todos elementos ao layout principal
        layout.add_widget(topbar)
        layout.add_widget(tabs_layout)
        layout.add_widget(self.content_area)
        
        # Salvar referência aos botões de abas
        self.btn_listar = btn_listar
        self.btn_cadastrar = btn_cadastrar
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        """Atualizar posição do retângulo de fundo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def voltar_menu(self, instance):
        """Voltar para a tela de menu"""
        self.manager.current = 'menu'
    
    def mudar_aba(self, aba):
        """Mudar entre as abas de listar e cadastrar"""
        # Atualizar cores dos botões
        if aba == 'listar':
            self.btn_listar.background_color = get_color_from_hex(ROXO_ESCURO)
            self.btn_listar.color = get_color_from_hex(BRANCO)
            self.btn_cadastrar.background_color = get_color_from_hex(ROXO_CLARO)
            self.btn_cadastrar.color = get_color_from_hex(CINZA_ESCURO)
            self.mostrar_lista_animais()
        else:
            self.btn_cadastrar.background_color = get_color_from_hex(ROXO_ESCURO)
            self.btn_cadastrar.color = get_color_from_hex(BRANCO)
            self.btn_listar.background_color = get_color_from_hex(ROXO_CLARO)
            self.btn_listar.color = get_color_from_hex(CINZA_ESCURO)
            self.mostrar_formulario_cadastro()
    
    def mostrar_lista_animais(self):
        """Mostrar lista de animais do banco de dados"""
        # Limpar área de conteúdo
        self.content_area.clear_widgets()
        
        # Criar scroll view para lista
        scroll_view = ScrollView()
        list_layout = BoxLayout(orientation='vertical', 
                               spacing=dp(10), 
                               padding=dp(10),
                               size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        # Carregar animais do banco de dados
        animais = self.db_manager.query("SELECT * FROM animais ORDER BY data_cadastro DESC")
        
        if not animais:
            # Mensagem quando não há animais
            msg_layout = BoxLayout(orientation='vertical', 
                                  size_hint_y=None, height=dp(100))
            msg = Label(text="Não há animais cadastrados.\nUtilize a aba 'Cadastrar' para adicionar.",
                       color=get_color_from_hex(CINZA_ESCURO))
            msg_layout.add_widget(msg)
            list_layout.add_widget(msg_layout)
        else:
            # Adicionar cards para cada animal
            for animal in animais:
                card = self.criar_card_animal(dict(animal))
                list_layout.add_widget(card)
        
        # Adicionar layout ao scroll view
        scroll_view.add_widget(list_layout)
        
        # Adicionar scroll view à área de conteúdo
        self.content_area.add_widget(scroll_view)
    
    def criar_card_animal(self, animal):
        """Criar card para exibir informações do animal"""
        card = BoxLayout(orientation='vertical',
                        size_hint_y=None, height=dp(150),
                        padding=dp(10), spacing=dp(5))
        
        # Adicionar fundo e borda
        with card.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(*get_color_from_hex(BRANCO))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(5)])
            Color(*get_color_from_hex(ROXO_CLARO))
            Line(rounded_rectangle=[card.pos[0], card.pos[1], card.size[0], card.size[1], dp(5)], width=1.5)
            card.bind(pos=self.update_card_rect, size=self.update_card_rect)
        
        # Layout para ID e tipo
        header = BoxLayout(orientation='horizontal',
                          size_hint_y=None, height=dp(30))
        
        lbl_id = Label(text=f"ID: {animal['codigo']}",
                      color=get_color_from_hex(ROXO_PRIMARIO),
                      font_size=dp(16),
                      bold=True,
                      size_hint_x=0.5,
                      halign='left',
                      text_size=(card.width / 2, None))
        
        lbl_tipo = Label(text=animal['tipo'],
                        color=get_color_from_hex(CINZA_ESCURO),
                        font_size=dp(14),
                        size_hint_x=0.5,
                        halign='right',
                        text_size=(card.width / 2, None))
        
        header.add_widget(lbl_id)
        header.add_widget(lbl_tipo)
        
        # Informações do animal
        lbl_nascimento = Label(text=f"Nascimento: {animal['nascimento']}",
                              color=get_color_from_hex(CINZA_ESCURO),
                              font_size=dp(14),
                              size_hint_y=None, height=dp(25),
                              halign='left',
                              text_size=(card.width, None))
        
        lbl_raca = Label(text=f"Raça: {animal['raca']}",
                        color=get_color_from_hex(CINZA_ESCURO),
                        font_size=dp(14),
                        size_hint_y=None, height=dp(25),
                        halign='left',
                        text_size=(card.width, None))
        
        # Cor diferente para status
        cor_status = "#4CAF50" if animal['status'] == "Ativo" else "#F44336"
        lbl_status = Label(text=f"Status: {animal['status']}",
                          color=get_color_from_hex(cor_status),
                          font_size=dp(14),
                          size_hint_y=None, height=dp(25),
                          halign='left',
                          text_size=(card.width, None))
        
        # Botões de ação
        acoes = BoxLayout(orientation='horizontal',
                         size_hint_y=None, height=dp(40),
                         spacing=dp(10))
        
        btn_detalhes = Button(text='Detalhes',
                            background_color=get_color_from_hex(ROXO_PRIMARIO),
                            color=get_color_from_hex(BRANCO),
                            size_hint_x=0.5)
        btn_detalhes.bind(on_press=lambda x, id=animal['id']: self.mostrar_detalhes(id))
        
        btn_editar = Button(text='Editar',
                          background_color=get_color_from_hex(CINZA_CLARO),
                          color=get_color_from_hex(CINZA_ESCURO),
                          size_hint_x=0.5)
        btn_editar.bind(on_press=lambda x, id=animal['id']: self.editar_animal(id))
        
        acoes.add_widget(btn_detalhes)
        acoes.add_widget(btn_editar)
        
        # Adicionar todos elementos ao card
        card.add_widget(header)
        card.add_widget(lbl_nascimento)
        card.add_widget(lbl_raca)
        card.add_widget(lbl_status)
        card.add_widget(acoes)
        
        return card
    
    def update_card_rect(self, instance, value):
        """Atualizar os retângulos do card quando ele muda de tamanho/posição"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            from kivy.graphics import Color, RoundedRectangle, Line
            Color(*get_color_from_hex(BRANCO))
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(5)])
            Color(*get_color_from_hex(ROXO_CLARO))
            Line(rounded_rectangle=[instance.pos[0], instance.pos[1], instance.size[0], instance.size[1], dp(5)], width=1.5)
    
    def mostrar_formulario_cadastro(self):
        """Mostrar formulário de cadastro de animais"""
        # Limpar área de conteúdo
        self.content_area.clear_widgets()
        
        # Criar scroll view para formulário
        scroll_view = ScrollView()
        form_layout = BoxLayout(orientation='vertical', 
                               spacing=dp(15), 
                               padding=dp(20),
                               size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Título do formulário
        titulo = Label(text='Cadastro de Novo Animal',
                      font_size=dp(20),
                      color=get_color_from_hex(ROXO_PRIMARIO),
                      size_hint_y=None, height=dp(50))
        
        # Campos do formulário
        # Tipo de animal
        lbl_tipo = Label(text='Tipo de Animal:',
                        font_size=dp(16),
                        color=get_color_from_hex(CINZA_ESCURO),
                        size_hint_y=None, height=dp(30),
                        halign='left',
                        text_size=(400, None))
        
        self.spinner_tipo = SpinnerWidget(
            text='Selecione',
            values=('Porca', 'Cachaço', 'Leitão', 'Leitoa'),
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(CINZA_CLARO),
            color=get_color_from_hex(CINZA_ESCURO)
        )
        
        # Identificação
        lbl_identificacao = Label(text='Identificação:',
                                font_size=dp(16),
                                color=get_color_from_hex(CINZA_ESCURO),
                                size_hint_y=None, height=dp(30),
                                halign='left',
                                text_size=(400, None))
        
        self.input_identificacao = TextInput(
            hint_text='Digite a identificação do animal',
            multiline=False,
            size_hint_y=None, height=dp(50),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Data de nascimento
        lbl_nascimento = Label(text='Data de Nascimento:',
                              font_size=dp(16),
                              color=get_color_from_hex(CINZA_ESCURO),
                              size_hint_y=None, height=dp(30),
                              halign='left',
                              text_size=(400, None))
        
        self.input_nascimento = TextInput(
            hint_text='DD/MM/AAAA',
            multiline=False,
            size_hint_y=None, height=dp(50),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Raça
        lbl_raca = Label(text='Raça:',
                        font_size=dp(16),
                        color=get_color_from_hex(CINZA_ESCURO),
                        size_hint_y=None, height=dp(30),
                        halign='left',
                        text_size=(400, None))
        
        self.spinner_raca = SpinnerWidget(
            text='Selecione',
            values=('Landrace', 'Large White', 'Duroc', 'Pietrain', 'Híbrido'),
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(CINZA_CLARO),
            color=get_color_from_hex(CINZA_ESCURO)
        )
        
        # Status
        lbl_status = Label(text='Status:',
                          font_size=dp(16),
                          color=get_color_from_hex(CINZA_ESCURO),
                          size_hint_y=None, height=dp(30),
                          halign='left',
                          text_size=(400, None))
        
        self.spinner_status = SpinnerWidget(
            text='Ativo',
            values=('Ativo', 'Inativo'),
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(CINZA_CLARO),
            color=get_color_from_hex(CINZA_ESCURO)
        )
        
        # Peso ao nascimento
        lbl_peso = Label(text='Peso ao Nascimento (kg):',
                        font_size=dp(16),
                        color=get_color_from_hex(CINZA_ESCURO),
                        size_hint_y=None, height=dp(30),
                        halign='left',
                        text_size=(400, None))
        
        self.input_peso = TextInput(
            hint_text='0.00',
            multiline=False,
            input_filter='float',
            size_hint_y=None, height=dp(50),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Observações
        lbl_obs = Label(text='Observações:',
                       font_size=dp(16),
                       color=get_color_from_hex(CINZA_ESCURO),
                       size_hint_y=None, height=dp(30),
                       halign='left',
                       text_size=(400, None))
        
        self.input_obs = TextInput(
            hint_text='Informações adicionais sobre o animal',
            multiline=True,
            size_hint_y=None, height=dp(100),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Botão de salvar
        btn_salvar = Button(text='Salvar Animal',
                          size_hint_y=None, height=dp(50),
                          background_color=get_color_from_hex(ROXO_PRIMARIO),
                          color=get_color_from_hex(BRANCO))
        btn_salvar.bind(on_press=self.salvar_animal)
        
        # Espaço final
        espacador = BoxLayout(size_hint_y=None, height=dp(20))
        
        # Adicionar widgets ao formulário
        form_layout.add_widget(titulo)
        form_layout.add_widget(lbl_tipo)
        form_layout.add_widget(self.spinner_tipo)
        form_layout.add_widget(lbl_identificacao)
        form_layout.add_widget(self.input_identificacao)
        form_layout.add_widget(lbl_nascimento)
        form_layout.add_widget(self.input_nascimento)
        form_layout.add_widget(lbl_raca)
        form_layout.add_widget(self.spinner_raca)
        form_layout.add_widget(lbl_status)
        form_layout.add_widget(self.spinner_status)
        form_layout.add_widget(lbl_peso)
        form_layout.add_widget(self.input_peso)
        form_layout.add_widget(lbl_obs)
        form_layout.add_widget(self.input_obs)
        form_layout.add_widget(btn_salvar)
        form_layout.add_widget(espacador)
        
        # Adicionar formulário ao scroll view
        scroll_view.add_widget(form_layout)
        
        # Adicionar scroll view à área de conteúdo
        self.content_area.add_widget(scroll_view)
    
    def salvar_animal(self, instance):
        """Salvar dados do animal no banco de dados"""
        # Verificar se os campos obrigatórios estão preenchidos
        if (self.spinner_tipo.text == 'Selecione' or 
            not self.input_identificacao.text or 
            not self.input_nascimento.text or 
            self.spinner_raca.text == 'Selecione'):
            
            popup = Popup(title='Erro',
                        content=Label(text='Por favor, preencha todos os campos obrigatórios.'),
                        size_hint=(0.8, 0.3))
            popup.open()
            return
        
        try:
            # Verificar se o código já existe
            if self.db_manager.query("SELECT id FROM animais WHERE codigo = ?", 
                                    (self.input_identificacao.text,)):
                popup = Popup(title='Erro',
                            content=Label(text='Este código de identificação já está em uso.'),
                            size_hint=(0.8, 0.3))
                popup.open()
                return
            
            # Converter peso para float ou usar None se estiver vazio
            peso = None
            if self.input_peso.text:
                try:
                    peso = float(self.input_peso.text)
                except ValueError:
                    popup = Popup(title='Erro',
                                content=Label(text='O peso deve ser um número válido.'),
                                size_hint=(0.8, 0.3))
                    popup.open()
                    return
            
            # Inserir no banco de dados
            success = self.db_manager.execute(
                """
                INSERT INTO animais 
                (codigo, tipo, raca, nascimento, status, peso_nascimento, data_cadastro, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.input_identificacao.text,
                    self.spinner_tipo.text,
                    self.spinner_raca.text,
                    self.input_nascimento.text,
                    self.spinner_status.text,
                    peso,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    self.input_obs.text
                )
            )
            
            if success:
                # Mostrar popup de sucesso
                popup = Popup(title='Sucesso',
                            content=Label(text='Animal cadastrado com sucesso!'),
                            size_hint=(0.8, 0.3))
                popup.open()
                
                # Limpar formulário
                self.spinner_tipo.text = 'Selecione'
                self.input_identificacao.text = ''
                self.input_nascimento.text = ''
                self.spinner_raca.text = 'Selecione'
                self.spinner_status.text = 'Ativo'
                self.input_peso.text = ''
                self.input_obs.text = ''
                
                # Voltar para a lista
                Clock.schedule_once(lambda dt: self.mudar_aba('listar'), 1)
            else:
                popup = Popup(title='Erro',
                            content=Label(text='Erro ao salvar os dados. Tente novamente.'),
                            size_hint=(0.8, 0.3))
                popup.open()
        
        except Exception as e:
            popup = Popup(title='Erro',
                        content=Label(text=f'Erro: {str(e)}'),
                        size_hint=(0.8, 0.3))
            popup.open()
    
    def mostrar_detalhes(self, id_animal):
        """Mostrar detalhes do animal"""
        try:
            # Buscar dados do animal
            animal = self.db_manager.query("SELECT * FROM animais WHERE id = ?", (id_animal,))
            
            if animal:
                animal = dict(animal[0])
                
                # Criar conteúdo para o popup
                content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
                
                # Título
                titulo = Label(
                    text=f"Animal {animal['codigo']} - {animal['tipo']}",
                    font_size=dp(18),
                    color=get_color_from_hex(ROXO_PRIMARIO),
                    size_hint_y=None, height=dp(40),
                    bold=True
                )
                
                # Scroll para informações
                scroll = ScrollView()
                info_layout = BoxLayout(orientation='vertical', 
                                      spacing=dp(5), 
                                      size_hint_y=None)
                info_layout.bind(minimum_height=info_layout.setter('height'))
                
                # Adicionar informações
                info = [
                    f"Raça: {animal['raca']}",
                    f"Nascimento: {animal['nascimento']}",
                    f"Status: {animal['status']}",
                    f"Peso ao Nascimento: {animal['peso_nascimento'] or 'Não informado'} kg",
                    f"Data de Cadastro: {animal['data_cadastro']}",
                    f"Observações: {animal['observacoes'] or 'Nenhuma'}"
                ]
                
                for item in info:
                    lbl = Label(
                        text=item,
                        font_size=dp(14),
                        size_hint_y=None, height=dp(30),
                        text_size=(Window.width - dp(80), None),
                        halign='left'
                    )
                    info_layout.add_widget(lbl)
                
                # Botão de fechar
                btn_fechar = Button(
                    text='Fechar',
                    size_hint_y=None, height=dp(50),
                    background_color=get_color_from_hex(ROXO_PRIMARIO),
                    color=get_color_from_hex(BRANCO)
                )
                
                # Adicionar ao scroll
                scroll.add_widget(info_layout)
                
                # Adicionar elementos ao layout
                content.add_widget(titulo)
                content.add_widget(scroll)
                content.add_widget(btn_fechar)
                
                # Criar e mostrar popup
                popup = Popup(
                    title='Detalhes do Animal',
                    content=content,
                    size_hint=(0.9, 0.7)
                )
                
                # Configurar botão para fechar popup
                btn_fechar.bind(on_press=popup.dismiss)
                
                popup.open()
            else:
                popup = Popup(
                    title='Erro',
                    content=Label(text='Animal não encontrado.'),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
        
        except Exception as e:
            popup = Popup(
                title='Erro',
                content=Label(text=f'Erro ao carregar detalhes: {str(e)}'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
    
    def editar_animal(self, id_animal):
        """Editar animal existente"""
        # Em uma implementação real, aqui seria mostrado um formulário de edição
        # Para simplificar, apenas mostramos uma mensagem
        popup = Popup(
            title='Edição',
            content=Label(text='A funcionalidade de edição será implementada na próxima versão.'),
            size_hint=(0.8, 0.3)
        )
        popup.open()

# Classe para a tela de saúde
class SaudeScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super(SaudeScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # Barra superior
        topbar = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, height=dp(60),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Adicionar cor de fundo à barra superior
        with topbar.canvas.before:
            Color(*get_color_from_hex(ROXO_PRIMARIO))
            self.rect = Rectangle(pos=topbar.pos, size=topbar.size)
            topbar.bind(pos=self.update_rect, size=self.update_rect)
        
        # Botão voltar
        back_button = Button(
            text='←', 
            font_size=dp(24),
            size_hint_x=None, width=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO)
        )
        back_button.bind(on_press=self.voltar_menu)
        
        # Título na barra superior
        title_label = Label(
            text='Saúde Animal', 
            font_size=dp(18),
            color=get_color_from_hex(BRANCO)
        )
        
        # Adicionar widgets à barra superior
        topbar.add_widget(back_button)
        topbar.add_widget(title_label)
        
        # Conteúdo principal - mensagem de desenvolvimento
        content = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Ícone
        icon_layout = BoxLayout(size_hint_y=0.3)
        icon = Label(
            text="🏥",
            font_size=dp(60),
            color=get_color_from_hex(ROXO_PRIMARIO)
        )
        icon_layout.add_widget(icon)
        
        # Mensagem
        message = Label(
            text="O módulo de saúde está sendo desenvolvido.\n\nNa próxima versão, você poderá registrar e acompanhar:\n- Vacinações\n- Medicações\n- Doenças\n- Tratamentos\n- Histórico médico",
            font_size=dp(16),
            color=get_color_from_hex(CINZA_ESCURO),
            halign='center'
        )
        
        # Botão para voltar
        btn_voltar = Button(
            text='Voltar ao Menu',
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO),
            color=get_color_from_hex(BRANCO)
        )
        btn_voltar.bind(on_press=self.voltar_menu)
        
        # Adicionar elementos ao conteúdo
        content.add_widget(icon_layout)
        content.add_widget(message)
        content.add_widget(BoxLayout(size_hint_y=0.3))  # Espaço
        content.add_widget(btn_voltar)
        
        # Adicionar todos elementos ao layout principal
        layout.add_widget(topbar)
        layout.add_widget(content)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        """Atualizar posição do retângulo de fundo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def voltar_menu(self, instance):
        """Voltar para a tela de menu"""
        self.manager.current = 'menu'

# Classe para a tela de reprodução
class ReproducaoScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super(ReproducaoScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # Barra superior
        topbar = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, height=dp(60),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Adicionar cor de fundo à barra superior
        with topbar.canvas.before:
            Color(*get_color_from_hex(ROXO_PRIMARIO))
            self.rect = Rectangle(pos=topbar.pos, size=topbar.size)
            topbar.bind(pos=self.update_rect, size=self.update_rect)
        
        # Botão voltar
        back_button = Button(
            text='←', 
            font_size=dp(24),
            size_hint_x=None, width=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO)
        )
        back_button.bind(on_press=self.voltar_menu)
        
        # Título na barra superior
        title_label = Label(
            text='Reprodução', 
            font_size=dp(18),
            color=get_color_from_hex(BRANCO)
        )
        
        # Adicionar elementos à barra superior
        topbar.add_widget(back_button)
        topbar.add_widget(title_label)
        
        # Conteúdo principal - mensagem de desenvolvimento
        content = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Ícone
        icon_layout = BoxLayout(size_hint_y=0.3)
        icon = Label(
            text="🔄",
            font_size=dp(60),
            color=get_color_from_hex(ROXO_PRIMARIO)
        )
        icon_layout.add_widget(icon)
        
        # Mensagem
        message = Label(
            text="O módulo de reprodução está sendo desenvolvido.\n\nNa próxima versão, você poderá registrar e acompanhar:\n- Ciclos reprodutivos\n- Inseminações\n- Gestações\n- Partos\n- Leitegadas",
            font_size=dp(16),
            color=get_color_from_hex(CINZA_ESCURO),
            halign='center'
        )
        
        # Botão para voltar
        btn_voltar = Button(
            text='Voltar ao Menu',
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO),
            color=get_color_from_hex(BRANCO)
        )
        btn_voltar.bind(on_press=self.voltar_menu)
        
        # Adicionar elementos ao conteúdo
        content.add_widget(icon_layout)
        content.add_widget(message)
        content.add_widget(BoxLayout(size_hint_y=0.3))  # Espaço
        content.add_widget(btn_voltar)
        
        # Adicionar todos elementos ao layout principal
        layout.add_widget(topbar)
        layout.add_widget(content)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        """Atualizar posição do retângulo de fundo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def voltar_menu(self, instance):
        """Voltar para a tela de menu"""
        self.manager.current = 'menu'

# Classe para a tela de crescimento
class CrescimentoScreen(Screen):
    def __init__(self, db_manager, **kwargs):
        super(CrescimentoScreen, self).__init__(**kwargs)
        self.db_manager = db_manager
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # Barra superior
        topbar = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, height=dp(60),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Adicionar cor de fundo à barra superior
        with topbar.canvas.before:
            Color(*get_color_from_hex(ROXO_PRIMARIO))
            self.rect = Rectangle(pos=topbar.pos, size=topbar.size)
            topbar.bind(pos=self.update_rect, size=self.update_rect)
        
        # Botão voltar
        back_button = Button(
            text='←', 
            font_size=dp(24),
            size_hint_x=None, width=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO)
        )
        back_button.bind(on_press=self.voltar_menu)
        
        # Título na barra superior
        title_label = Label(
            text='Crescimento', 
            font_size=dp(18),
            color=get_color_from_hex(BRANCO)
        )
        
        # Adicionar elementos à barra superior
        topbar.add_widget(back_button)
        topbar.add_widget(title_label)
        
        # Conteúdo principal - mensagem de desenvolvimento
        content = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Ícone
        icon_layout = BoxLayout(size_hint_y=0.3)
        icon = Label(
            text="📈",
            font_size=dp(60),
            color=get_color_from_hex(ROXO_PRIMARIO)
        )
        icon_layout.add_widget(icon)
        
        # Mensagem
        message = Label(
            text="O módulo de crescimento está sendo desenvolvido.\n\nNa próxima versão, você poderá registrar e acompanhar:\n- Pesagens periódicas\n- Curvas de crescimento\n- Comparativos de ganho de peso\n- Conversão alimentar\n- Histórico de desenvolvimento",
            font_size=dp(16),
            color=get_color_from_hex(CINZA_ESCURO),
            halign='center'
        )
        
        # Botão para voltar
        btn_voltar = Button(
            text='Voltar ao Menu',
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO),
            color=get_color_from_hex(BRANCO)
        )
        btn_voltar.bind(on_press=self.voltar_menu)
        
        # Adicionar elementos ao conteúdo
        content.add_widget(icon_layout)
        content.add_widget(message)
        content.add_widget(BoxLayout(size_hint_y=0.3))  # Espaço
        content.add_widget(btn_voltar)
        
        # Adicionar todos elementos ao layout principal
        layout.add_widget(topbar)
        layout.add_widget(content)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        """Atualizar posição do retângulo de fundo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def voltar_menu(self, instance):
        """Voltar para a tela de menu"""
        self.manager.current = 'menu'

# Gerenciador de telas
class SuinoculturaApp(App):
    # Menu status
    menu_expanded = BooleanProperty(False)
    
    def build(self):
        # Configuração do app
        self.title = 'Sistema Suinocultura'
        self.icon = 'assets/logo_placeholder.png'
        
        # Carregar o arquivo KV
        Builder.load_file('kivy_app_offline/suinocultura.kv')
        
        # Criar gerenciador de banco de dados
        self.db_manager = DatabaseManager()
        
        # Criar gerenciador de usuários
        self.user_manager = UserManager(self.db_manager)
        
        # Criar gerenciador de telas principal
        self.app_screen_manager = ScreenManager(transition=FadeTransition())
        
        # Tela de login
        login_screen = Screen(name='login')
        login_screen.add_widget(Factory.LoginScreen())
        self.app_screen_manager.add_widget(login_screen)
        
        # Tela principal do app
        main_screen = Screen(name='main')
        main_screen.add_widget(Factory.MainScreen())
        self.app_screen_manager.add_widget(main_screen)
        
        # Inicializar animais e dados de exemplo
        self.initialize_sample_data()
        
        # Iniciar na tela de login
        return self.app_screen_manager
    
    def login(self, *args):
        """Autenticar usuário e navegar para tela principal"""
        error_label = self.app_screen_manager.get_screen('login').children[0].ids.error_label
        username = self.app_screen_manager.get_screen('login').children[0].ids.username_input.text
        password = self.app_screen_manager.get_screen('login').children[0].ids.password_input.text
        
        if not username:
            error_label.text = "Por favor, informe seu usuário"
            return
            
        # Verificar usuário no banco de dados
        users = self.db_manager.query("SELECT * FROM usuarios WHERE matricula = ?", (username,))
        
        if users:
            # Definir informações do usuário na tela principal
            main_screen = self.app_screen_manager.get_screen('main').children[0]
            user_info = dict(users[0])
            main_screen.ids.user_name.text = user_info['nome']
            main_screen.ids.user_role.text = f"Perfil: {user_info['cargo']}"
            
            # Navegar para tela principal com animação
            self.app_screen_manager.transition.direction = 'left'
            self.app_screen_manager.current = 'main'
            
            # Atualizar estatísticas
            self.update_statistics()
        else:
            error_label.text = "Usuário não encontrado"
    
    def logout(self):
        """Fazer logout e voltar para tela de login"""
        self.app_screen_manager.transition.direction = 'right'
        self.app_screen_manager.current = 'login'
        
        # Limpar campos
        login_screen = self.app_screen_manager.get_screen('login').children[0]
        login_screen.ids.username_input.text = ''
        login_screen.ids.password_input.text = ''
        login_screen.ids.error_label.text = ''
    
    def toggle_menu(self):
        """Mostrar/ocultar menu lateral"""
        side_menu = self.app_screen_manager.get_screen('main').children[0].ids.side_menu
        
        # Se o menu está fechado, abri-lo
        if side_menu.width == 0:
            self.menu_expanded = True
            anim = Animation(width=dp(250), opacity=1, duration=0.3, t='out_quad')
            anim.start(side_menu)
        # Se o menu está aberto, fechá-lo
        else:
            self.menu_expanded = False
            anim = Animation(width=0, opacity=0, duration=0.2, t='in_quad')
            anim.start(side_menu)
    
    def change_screen(self, screen_name):
        """Mudar para a tela especificada"""
        # Fechar menu ao mudar de tela
        if self.menu_expanded:
            self.toggle_menu()
        
        # Mudar para a tela especificada
        self.app_screen_manager.get_screen('main').children[0].ids.screen_manager.current = screen_name
    
    def open_sync_options(self):
        """Abrir opções de sincronização"""
        # Implementar popup de sincronização
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Título
        title = Label(
            text='Sincronização com Cloud',
            size_hint_y=None, height=dp(40),
            font_size=dp(18),
            color=get_color_from_hex(COR_TEXTO_PRIMARIO)
        )
        
        # Botões
        export_button = Factory.CustomButton(
            text='Exportar Dados',
            size_hint_y=None, height=dp(50),
            on_release=lambda x: self.start_sync_process(popup, 'export')
        )
        
        import_button = Factory.CustomButton(
            text='Importar Dados',
            size_hint_y=None, height=dp(50),
            on_release=lambda x: self.start_sync_process(popup, 'import')
        )
        
        cancel_button = Factory.CustomButton(
            text='Cancelar',
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex("#455A64"),
            on_release=lambda x: popup.dismiss()
        )
        
        # Adicionar widgets
        content.add_widget(title)
        content.add_widget(export_button)
        content.add_widget(import_button)
        content.add_widget(cancel_button)
        
        # Criar popup
        popup = Popup(
            title='Sincronização',
            content=content,
            size_hint=(0.9, None),
            height=dp(300),
            background_color=get_color_from_hex(COR_FUNDO),
            title_color=get_color_from_hex(COR_ACENTO),
            separator_color=get_color_from_hex(COR_PRIMARIA)
        )
        
        # Mostrar popup
        popup.open()
    
    def start_sync_process(self, popup, action):
        """Iniciar processo de sincronização (export ou import)"""
        popup.dismiss()
        
        # Feedback de sincronização 
        # (em um app real, implementar sincronização real com Firebase)
        status_label = self.app_screen_manager.get_screen('main').children[0].ids.sync_status
        status_label.text = '⌛'
        
        # Simular processamento (em um app real, fazer operação real em outra thread)
        Clock.schedule_once(lambda dt: self.finish_sync_process(action), 2)
    
    def finish_sync_process(self, action):
        """Finalizar processo de sincronização com feedback"""
        # Atualizar ícone de sincronização
        status_label = self.app_screen_manager.get_screen('main').children[0].ids.sync_status
        status_label.text = '✅'
        
        # Feedback ao usuário
        message = "Dados exportados com sucesso!" if action == 'export' else "Dados importados com sucesso!"
        
        # Mostrar popup de confirmação
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Mensagem
        msg_label = Label(
            text=message,
            size_hint_y=None, height=dp(60),
            font_size=dp(16),
            color=get_color_from_hex(COR_TEXTO_PRIMARIO)
        )
        
        # Botão de confirmação
        ok_button = Factory.CustomButton(
            text='OK',
            size_hint_y=None, height=dp(50),
            on_release=lambda x: popup.dismiss()
        )
        
        # Adicionar widgets
        content.add_widget(msg_label)
        content.add_widget(ok_button)
        
        # Criar popup
        popup = Popup(
            title='Sincronização Concluída',
            content=content,
            size_hint=(0.8, None),
            height=dp(200),
            background_color=get_color_from_hex(COR_FUNDO),
            title_color=get_color_from_hex(COR_ACENTO),
            separator_color=get_color_from_hex(COR_PRIMARIA)
        )
        
        # Mostrar popup
        popup.open()
        
        # Restaurar ícone original após 2 segundos
        Clock.schedule_once(lambda dt: setattr(status_label, 'text', '🔄'), 2)
    
    def open_animal_form(self):
        """Abrir formulário para cadastro de novo animal"""
        # Implementar formulário de cadastro
        pass
    
    def filter_animals(self, search_text):
        """Filtrar lista de animais pelo texto de busca"""
        # Implementar filtro na lista de animais
        pass
        
    def initialize_sample_data(self):
        """Inicializar dados de exemplo para demonstração"""
        # Adicionar alguns animais de exemplo se a tabela estiver vazia
        animals = self.db_manager.query("SELECT COUNT(*) as count FROM animais")
        
        if animals[0]['count'] == 0:
            # Inserir dados de exemplo
            sample_animals = [
                ('A001', 'Porca', 'Landrace', '2023-01-15', 'Ativo', 1.5, '2023-01-20', 'Animal saudável'),
                ('A002', 'Porca', 'Yorkshire', '2023-02-10', 'Ativo', 1.3, '2023-02-15', 'Animal saudável'),
                ('A003', 'Porca', 'Duroc', '2023-03-05', 'Ativo', 1.6, '2023-03-10', 'Animal saudável'),
                ('A004', 'Varraco', 'Pietrain', '2023-01-25', 'Ativo', 1.7, '2023-01-30', 'Animal reprodutor'),
                ('A005', 'Leitão', 'Landrace', '2023-04-20', 'Ativo', 0.8, '2023-04-25', 'Leitão saudável')
            ]
            
            self.db_manager.executemany(
                "INSERT INTO animais (codigo, tipo, raca, nascimento, status, peso_nascimento, data_cadastro, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                sample_animals
            )
            
            # Adicionar eventos de reprodução de exemplo
            sample_reproduction = [
                (1, 'Cio', '2023-05-15', 'Primeiro cio detectado'),
                (2, 'Cio', '2023-05-20', 'Cio normal'),
                (3, 'Inseminação', '2023-05-25', 'Inseminação artificial realizada')
            ]
            
            self.db_manager.executemany(
                "INSERT INTO reproducao (id_animal, tipo_evento, data_evento, observacoes) VALUES (?, ?, ?, ?)",
                sample_reproduction
            )
            
            print("Dados de exemplo inicializados com sucesso!")
    
    def update_statistics(self):
        """Atualizar estatísticas na tela inicial"""
        try:
            # Obter dados do banco
            main_screen = self.app_screen_manager.get_screen('main').children[0].ids.screen_manager.get_screen('home')
            
            # Total de animais
            total = self.db_manager.query("SELECT COUNT(*) as count FROM animais")[0]['count']
            main_screen.ids.total_animals.text = str(total)
            
            # Animais em cio
            in_heat = self.db_manager.query("SELECT COUNT(*) as count FROM reproducao WHERE tipo_evento = 'Cio' AND data_evento >= date('now', '-7 days')")[0]['count']
            main_screen.ids.animals_in_heat.text = str(in_heat)
            
            # Preencher eventos recentes (últimos 5)
            events_container = main_screen.ids.events_container
            events_container.clear_widgets()
            
            recent_events = self.db_manager.query("""
                SELECT r.tipo_evento, r.data_evento, a.codigo, a.tipo
                FROM reproducao r
                JOIN animais a ON r.id_animal = a.id
                ORDER BY r.data_evento DESC
                LIMIT 5
            """)
            
            if recent_events:
                for event in recent_events:
                    # Criar card para o evento
                    card = BoxLayout(
                        orientation='vertical',
                        size_hint_y=None,
                        height=dp(80),
                        padding=dp(10),
                        spacing=dp(5)
                    )
                    
                    # Configurar aparência do card
                    with card.canvas.before:
                        Color(*get_color_from_hex(COR_SUPERFICIE))
                        RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
                    
                    # Cabeçalho com tipo de evento e data
                    header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                    
                    # Tipo de evento
                    event_type = Label(
                        text=event['tipo_evento'],
                        font_size=dp(16),
                        color=get_color_from_hex(COR_ACENTO),
                        bold=True,
                        size_hint_x=0.7,
                        halign='left',
                        text_size=(Window.width * 0.5, None)
                    )
                    
                    # Data do evento
                    event_date = Label(
                        text=event['data_evento'],
                        font_size=dp(14),
                        color=get_color_from_hex(COR_TEXTO_SECUNDARIO),
                        size_hint_x=0.3,
                        halign='right',
                        text_size=(Window.width * 0.3, None)
                    )
                    
                    header.add_widget(event_type)
                    header.add_widget(event_date)
                    
                    # Informações do animal
                    animal_info = Label(
                        text=f"{event['tipo']} - {event['codigo']}",
                        font_size=dp(14),
                        color=get_color_from_hex(COR_TEXTO_PRIMARIO),
                        size_hint_y=None,
                        height=dp(20),
                        halign='left',
                        text_size=(Window.width * 0.8, None)
                    )
                    
                    # Adicionar elementos ao card
                    card.add_widget(header)
                    card.add_widget(animal_info)
                    
                    # Adicionar card ao container
                    events_container.add_widget(card)
            else:
                # Mensagem se não houver eventos
                no_events = Label(
                    text="Nenhum evento recente",
                    font_size=dp(16),
                    color=get_color_from_hex(COR_TEXTO_SECUNDARIO),
                    size_hint_y=None,
                    height=dp(40)
                )
                events_container.add_widget(no_events)
                
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
            
    def on_stop(self):
        """Executado quando o aplicativo é fechado"""
        # Fechar conexão com o banco de dados
        if hasattr(self, 'db_manager'):
            self.db_manager.close()


if __name__ == '__main__':
    try:
        # Criar diretório de assets se não existir
        import os
        if not os.path.exists('kivy_app_offline/assets'):
            os.makedirs('kivy_app_offline/assets')
        
        # Criar um logo placeholder SVG (mais moderno e sem dependências)
        if not os.path.exists('kivy_app_offline/assets/logo_placeholder.svg'):
            # Criar um SVG simples como logo
            svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <circle cx="100" cy="100" r="90" fill="{COR_PRIMARIA}" />
    <circle cx="100" cy="100" r="70" fill="{COR_SECUNDARIA}" />
    <text x="100" y="120" font-family="Arial" font-size="80" fill="{COR_TEXTO_PRIMARIO}" text-anchor="middle">S</text>
    <path d="M20,100 C20,40 180,40 180,100 C180,160 20,160 20,100 Z" fill="none" stroke="{COR_ACENTO}" stroke-width="5" opacity="0.5" />
</svg>'''
            
            # Salvar o SVG
            with open('kivy_app_offline/assets/logo_placeholder.svg', 'w') as f:
                f.write(svg_content)
            
            print("Logo SVG criado com sucesso!")
            
        # Manter o PNG também para compatibilidade
        if not os.path.exists('kivy_app_offline/assets/logo_placeholder.png'):
            try:
                # Criar um PNG colorido simples sem usar PIL
                import base64
                
                # Imagem base64 mínima de 1px (será redimensionada pelo Kivy)
                # Um pixel roxo em base64
                pixel_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFeAKQEurnDQAAAABJRU5ErkJggg=="
                
                # Decodificar e salvar
                with open('kivy_app_offline/assets/logo_placeholder.png', 'wb') as f:
                    f.write(base64.b64decode(pixel_data))
                
                print("Logo PNG criado com sucesso!")
            except Exception as e:
                print(f"Erro ao criar logo PNG: {e}")
        
        # Criar um arquivo de configuração local
        if not os.path.exists('kivy_app_offline/config.json'):
            config = {
                "theme": "dark",
                "accent_color": COR_ACENTO,
                "primary_color": COR_PRIMARIA,
                "app_version": "1.0.0",
                "database_path": "suinocultura.db",
                "sync_enabled": True,
                "last_sync": None
            }
            
            with open('kivy_app_offline/config.json', 'w') as f:
                import json
                json.dump(config, f, indent=4)
            
            print("Arquivo de configuração criado com sucesso!")
    except Exception as e:
        print(f"Erro ao configurar assets: {e}")
        
    # Executar a aplicação com tema escuro atualizado
    app = SuinoculturaApp()
    app.run()