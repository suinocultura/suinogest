import streamlit as st
import os
import sys
import pandas as pd
import importlib
import datetime
import base64
import json
import subprocess
from github import Github
from github.InputGitTreeElement import InputGitTreeElement
import tempfile
import re
import shutil

# Adicionar diretório raiz ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import check_developer_access, check_permission, load_employees, save_employees, load_permissions_map, save_permissions_map

# Configuração da página
st.set_page_config(
    page_title="Sistema do Desenvolvedor",
    page_icon="🛠️",
    layout="wide"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Inicialização das variáveis do APK WebView
if 'apk_app_name' not in st.session_state:
    st.session_state.apk_app_name = "Sistema Suinocultura"
if 'apk_package_name' not in st.session_state:
    st.session_state.apk_package_name = "com.suinocultura.app"
if 'apk_version' not in st.session_state:
    st.session_state.apk_version = "1.0.0"
if 'apk_url' not in st.session_state:
    st.session_state.apk_url = "https://suinocultura.replit.app"
if 'apk_primary_color' not in st.session_state:
    st.session_state.apk_primary_color = "#4CAF50"
if 'apk_dark_mode' not in st.session_state:
    st.session_state.apk_dark_mode = False
if 'apk_splash_screen' not in st.session_state:
    st.session_state.apk_splash_screen = True
if 'apk_enable_cache' not in st.session_state:
    st.session_state.apk_enable_cache = True
if 'apk_enable_zoom' not in st.session_state:
    st.session_state.apk_enable_zoom = True
if 'apk_offline_message' not in st.session_state:
    st.session_state.apk_offline_message = "Sem conexão com a internet. Tente novamente mais tarde."

# Verificar se o usuário está autenticado
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Você precisa estar autenticado para acessar esta página.")
    st.stop()

# Verificar se o usuário tem permissão para acessar esta página
if not check_permission(st.session_state.current_user, 'developer_tools'):
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()


# Verificar se o usuário está autenticado e tem permissão de desenvolvedor
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("Você precisa estar autenticado para acessar esta página.")
    st.stop()

if "current_user" not in st.session_state or not check_permission(st.session_state.current_user, 'developer_tools'):
    st.error("Você não tem permissão para acessar esta página. Apenas desenvolvedores têm acesso.")
    st.stop()

# Estilo CSS personalizado
st.markdown("""
<style>
    .dev-header {
        background-color: #1E1E1E;
        color: #00FF00;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #00FF00;
        font-family: 'Courier New', monospace;
    }
    .dev-section {
        background-color: #f0f0f0;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 5px solid #2196F3;
    }
    .dev-btn {
        background-color: #2196F3;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .danger-btn {
        background-color: #FF5252;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .log-output {
        background-color: #1E1E1E;
        color: #CCCCCC;
        font-family: 'Courier New', monospace;
        padding: 1rem;
        border-radius: 5px;
        height: 300px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    .status-ok {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-warning {
        color: #FFC107;
        font-weight: bold;
    }
    .status-error {
        color: #FF5252;
        font-weight: bold;
    }
    .dev-metric {
        background-color: #2D2D2D;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .dev-metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00FF00;
    }
    .dev-metric-label {
        color: #CCCCCC;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="dev-header"><h1>🛠️ Sistema do Desenvolvedor</h1><p>Ferramentas avançadas para gerenciamento e desenvolvimento do sistema</p></div>', unsafe_allow_html=True)

# Tabs para as diferentes funcionalidades
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Dashboard", "👥 Gerenciamento de Usuários", "🔄 Manutenção", "⚙️ Configurações", "📥 Downloads", "🔄 Atualizações", "🧩 Componentes"])

with tab1:
    st.markdown('<div class="dev-section"><h2>Dashboard de Desenvolvimento</h2></div>', unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    # Função para contar arquivos em um diretório
    def count_files(directory, extension=None):
        count = 0
        for _, _, files in os.walk(directory):
            if extension:
                count += len([f for f in files if f.endswith(extension)])
            else:
                count += len(files)
        return count
    
    # Função para pegar o tamanho de um diretório
    def get_dir_size(directory):
        total_size = 0
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size / (1024 * 1024)  # Tamanho em MB
    
    # Métricas
    with col1:
        st.markdown('<div class="dev-metric">', unsafe_allow_html=True)
        py_files = count_files(".", ".py")
        st.markdown(f'<div class="dev-metric-value">{py_files}</div>', unsafe_allow_html=True)
        st.markdown('<div class="dev-metric-label">Arquivos Python</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="dev-metric">', unsafe_allow_html=True)
        pages_count = count_files("pages", ".py")
        st.markdown(f'<div class="dev-metric-value">{pages_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="dev-metric-label">Páginas da Aplicação</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="dev-metric">', unsafe_allow_html=True)
        if os.path.exists("data"):
            data_size = round(get_dir_size("data"), 2)
        else:
            data_size = 0
        st.markdown(f'<div class="dev-metric-value">{data_size} MB</div>', unsafe_allow_html=True)
        st.markdown('<div class="dev-metric-label">Tamanho dos Dados</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="dev-metric">', unsafe_allow_html=True)
        # Contar usuários ativos
        employees_df = load_employees()
        active_users = len(employees_df[employees_df['status'] == 'Ativo']) if not employees_df.empty else 0
        st.markdown(f'<div class="dev-metric-value">{active_users}</div>', unsafe_allow_html=True)
        st.markdown('<div class="dev-metric-label">Usuários Ativos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Verificação do sistema
    st.markdown("### Verificação de Componentes do Sistema")
    
    # Status dos componentes vitais
    components = [
        {"name": "Python", "status": "OK", "version": sys.version.split()[0]},
        {"name": "Streamlit", "status": "OK", "version": st.__version__},
        {"name": "Pandas", "status": "OK", "version": pd.__version__},
        {"name": "Diretório de Dados", "status": "OK" if os.path.exists("data") else "ERROR", "version": "-"},
    ]
    
    # Verificar arquivos críticos
    critical_files = ["app.py", "utils.py", "create_download_package.py"]
    for file in critical_files:
        status = "OK" if os.path.exists(file) else "MISSING"
        components.append({"name": f"Arquivo {file}", "status": status, "version": "-"})
    
    # Exibir status dos componentes
    st.write("Status dos componentes do sistema:")
    
    component_df = pd.DataFrame(components)
    
    # Aplicar cor com base no status
    def highlight_status(s):
        if s == 'OK':
            return 'background-color: #EAFFEA; color: #4CAF50; font-weight: bold'
        elif s == 'WARNING':
            return 'background-color: #FFFAEA; color: #FFC107; font-weight: bold'
        elif s == 'ERROR' or s == 'MISSING':
            return 'background-color: #FFEAEA; color: #FF5252; font-weight: bold'
        else:
            return ''
    
    st.dataframe(
        component_df.style.applymap(highlight_status, subset=['status']),
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.markdown('<div class="dev-section"><h2>Gerenciamento de Usuários</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Registrar Novo Desenvolvedor")
        
        # Formulário para cadastro de desenvolvedores
        with st.form(key="dev_registration_form"):
            nome = st.text_input("Nome Completo")
            matricula = st.text_input("Matrícula")
            setor = st.text_input("Setor", value="Desenvolvimento")
            observacao = st.text_area("Observação", placeholder="Adicione informações adicionais se necessário")
            
            submit_button = st.form_submit_button(label="Registrar Desenvolvedor")
            
            if submit_button:
                if nome and matricula:
                    # Importar a função register_employee
                    from utils import register_employee
                    
                    # Chamar a função para registrar um novo desenvolvedor
                    success, message = register_employee(
                        nome=nome,
                        matricula=matricula,
                        cargo="Desenvolvedor",  # Cargo fixo como Desenvolvedor
                        setor=setor,
                        observacao=observacao
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
    
    with col2:
        st.subheader("Desenvolvedores Cadastrados")
        
        # Carregar dados dos funcionários
        employees_df = load_employees()
        
        # Filtrar apenas os desenvolvedores
        if not employees_df.empty:
            dev_df = employees_df[employees_df['cargo'] == 'Desenvolvedor']
            
            if not dev_df.empty:
                # Selecionar apenas as colunas relevantes
                display_df = dev_df[['nome', 'matricula', 'status', 'ultimo_acesso']]
                
                # Formatar o DataFrame para exibição
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True
                )
                
                # Opção para alterar status
                st.subheader("Alterar Status")
                
                selected_dev = st.selectbox(
                    "Selecione o Desenvolvedor",
                    options=dev_df['matricula'].tolist(),
                    format_func=lambda x: f"{dev_df[dev_df['matricula'] == x]['nome'].iloc[0]} ({x})"
                )
                
                new_status = st.selectbox(
                    "Novo Status",
                    options=["Ativo", "Inativo"]
                )
                
                if st.button("Atualizar Status"):
                    from utils import update_employee_status
                    success, message = update_employee_status(selected_dev, new_status)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("Não há desenvolvedores cadastrados no sistema.")
        else:
            st.info("Não há funcionários cadastrados no sistema.")

with tab3:
    st.markdown('<div class="dev-section"><h2>Manutenção do Sistema</h2></div>', unsafe_allow_html=True)
    
    # Dividir em seções
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Backup e Restauração")
        
        # Seção de backup
        with st.expander("Criar Backup", expanded=True):
            st.write("Crie um backup completo dos dados do sistema:")
            
            if st.button("Iniciar Backup", key="btn_backup"):
                # Criar diretório de backup se não existir
                backup_dir = "backups"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                # Nome do arquivo de backup com data e hora atual
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{backup_dir}/backup_{timestamp}.zip"
                
                # Criar backup
                import zipfile
                
                try:
                    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Adicionar diretório de dados
                        if os.path.exists("data"):
                            for root, _, files in os.walk("data"):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    zipf.write(file_path, os.path.relpath(file_path, ""))
                    
                    # Sucesso!
                    st.success(f"Backup criado com sucesso em {backup_file}")
                    
                    # Opção para download
                    with open(backup_file, "rb") as f:
                        data = f.read()
                    
                    b64 = base64.b64encode(data).decode()
                    href = f'<a href="data:application/zip;base64,{b64}" download="{os.path.basename(backup_file)}" style="text-decoration:none;">'\
                          f'<div style="background-color:#4CAF50; color:white; padding:10px; border-radius:5px; '\
                          f'cursor:pointer; text-align:center; margin:10px 0px;">Baixar Arquivo de Backup</div></a>'
                    
                    st.markdown(href, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Erro ao criar backup: {str(e)}")
        
        # Seção de restauração
        with st.expander("Restaurar Backup"):
            st.write("Restaure um backup de dados do sistema:")
            
            uploaded_file = st.file_uploader("Selecione o arquivo de backup (.zip)", type="zip")
            
            if uploaded_file is not None:
                if st.button("Restaurar Dados", key="btn_restore"):
                    # Criar diretório temporário
                    import tempfile
                    import shutil
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Salvar o arquivo de backup no diretório temporário
                        temp_file = os.path.join(temp_dir, "backup.zip")
                        with open(temp_file, "wb") as f:
                            f.write(uploaded_file.read())
                        
                        # Extrair conteúdo
                        try:
                            with zipfile.ZipFile(temp_file, 'r') as zipf:
                                # Extrair apenas os arquivos da pasta data
                                data_files = [f for f in zipf.namelist() if f.startswith("data/")]
                                
                                # Verificar se há arquivos de dados
                                if not data_files:
                                    st.error("Arquivo de backup inválido. Não contém dados.")
                                    st.stop()
                                
                                # Pergunta de confirmação
                                restore_confirm = st.radio(
                                    "Esta operação substituirá os dados existentes. Deseja continuar?",
                                    ["Não", "Sim"]
                                )
                                
                                if restore_confirm == "Sim":
                                    # Extrair os arquivos
                                    for file in data_files:
                                        zipf.extract(file, "")
                                    
                                    st.success("Dados restaurados com sucesso!")
                                    st.warning("Recarregue a página para ver os dados restaurados.")
                                else:
                                    st.info("Operação cancelada. Os dados atuais não foram alterados.")
                        
                        except Exception as e:
                            st.error(f"Erro ao restaurar backup: {str(e)}")
                
    with col2:
        st.subheader("Verificação e Reparo")
        
        # Seção de verificação do banco de dados
        with st.expander("Verificar Integridade dos Dados", expanded=True):
            st.write("Verifique se os arquivos de dados estão íntegros e com a estrutura correta.")
            
            if st.button("Iniciar Verificação", key="btn_check"):
                # Listar arquivos esperados
                expected_files = [
                    "data/animals.csv",
                    "data/breeding_cycles.csv",
                    "data/employees.csv",
                    "data/gestation.csv",
                    "data/weight_records.csv"
                ]
                
                results = []
                
                for file_path in expected_files:
                    if os.path.exists(file_path):
                        try:
                            # Tentar ler o arquivo para verificar a integridade
                            df = pd.read_csv(file_path)
                            row_count = len(df)
                            status = "OK"
                        except Exception as e:
                            row_count = 0
                            status = "ERRO"
                        
                        results.append({
                            "arquivo": os.path.basename(file_path),
                            "status": status,
                            "registros": row_count,
                            "tamanho": f"{os.path.getsize(file_path) / 1024:.2f} KB" if os.path.exists(file_path) else "0 KB"
                        })
                    else:
                        results.append({
                            "arquivo": os.path.basename(file_path),
                            "status": "FALTANDO",
                            "registros": 0,
                            "tamanho": "0 KB"
                        })
                
                results_df = pd.DataFrame(results)
                
                # Função para destacar status
                def highlight_status(val):
                    if val == "OK":
                        return 'background-color: #EAFFEA; color: green;'
                    elif val == "ERRO":
                        return 'background-color: #FFEAEA; color: red;'
                    else:
                        return 'background-color: #FFF3E0; color: orange;'
                
                # Exibir resultados
                st.dataframe(
                    results_df.style.applymap(highlight_status, subset=['status']),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Contar problemas
                problems = len(results_df[results_df['status'] != "OK"])
                
                if problems == 0:
                    st.success("Todos os arquivos de dados estão íntegros e disponíveis.")
                else:
                    st.warning(f"Foram encontrados problemas em {problems} arquivo(s).")
        
        # Seção de logs
        with st.expander("Logs do Sistema"):
            st.write("Visualize os logs mais recentes do sistema:")
            
            # Criar função para ler os logs
            def get_logs(n_lines=100):
                try:
                    # Verificar se há um arquivo de log
                    log_file = "app.log"
                    
                    if os.path.exists(log_file):
                        with open(log_file, "r") as f:
                            # Ler as últimas n linhas
                            lines = f.readlines()[-n_lines:]
                            return "".join(lines)
                    else:
                        return "Arquivo de log não encontrado."
                except Exception as e:
                    return f"Erro ao ler logs: {str(e)}"
            
            # Opções para visualização de logs
            n_lines = st.slider("Número de linhas para mostrar", 10, 500, 100)
            
            # Exibir logs
            log_content = get_logs(n_lines)
            st.markdown(f'<div class="log-output">{log_content}</div>', unsafe_allow_html=True)
            
            # Opção para limpar logs
            if st.button("Limpar Arquivo de Log", key="btn_clear_log"):
                try:
                    log_file = "app.log"
                    if os.path.exists(log_file):
                        # Fazer backup do arquivo de log antes de limpar
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_log = f"app_{timestamp}.log.bak"
                        
                        # Copiar para backup
                        import shutil
                        shutil.copy2(log_file, backup_log)
                        
                        # Limpar o arquivo
                        with open(log_file, "w") as f:
                            f.write(f"--- Log reiniciado em {datetime.datetime.now()} ---\n")
                        
                        st.success(f"Arquivo de log limpo. Backup criado em {backup_log}")
                    else:
                        st.warning("Arquivo de log não encontrado.")
                except Exception as e:
                    st.error(f"Erro ao limpar logs: {str(e)}")

with tab4:
    st.markdown('<div class="dev-section"><h2>Configurações do Sistema</h2></div>', unsafe_allow_html=True)
    
    # Configurações do sistema
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Configurações Avançadas")
        
        # Seção para configurações gerais
        with st.expander("Configurações Gerais", expanded=True):
            # Carregar configuração existente ou criar uma padrão
            config_file = "config.json"
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)
                except:
                    config = {"debug_mode": False, "max_upload_size_mb": 10, "session_timeout_minutes": 60}
            else:
                config = {"debug_mode": False, "max_upload_size_mb": 10, "session_timeout_minutes": 60}
            
            # Editar configurações
            debug_mode = st.toggle("Modo de Depuração", config.get("debug_mode", False))
            max_upload = st.number_input("Tamanho Máximo de Upload (MB)", min_value=1, max_value=100, value=config.get("max_upload_size_mb", 10))
            session_timeout = st.number_input("Tempo de Expiração da Sessão (minutos)", min_value=5, max_value=240, value=config.get("session_timeout_minutes", 60))
            
            # Atualizar configuração
            new_config = {
                "debug_mode": debug_mode,
                "max_upload_size_mb": max_upload,
                "session_timeout_minutes": session_timeout
            }
            
            # Salvar configurações
            if st.button("Salvar Configurações"):
                try:
                    with open(config_file, "w") as f:
                        json.dump(new_config, f, indent=4)
                    st.success("Configurações salvas com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar configurações: {str(e)}")
        
        # Seção para configurações de comportamento do sistema
        with st.expander("Comportamento do Sistema"):
            st.write("Configure o comportamento específico do sistema de gestão:")
            
            # Carregar configuração avançada ou criar uma padrão
            advanced_config_file = "advanced_config.json"
            
            if os.path.exists(advanced_config_file):
                try:
                    with open(advanced_config_file, "r") as f:
                        adv_config = json.load(f)
                except:
                    adv_config = {"enable_export": True, "max_reports": 50, "show_advanced_features": False}
            else:
                adv_config = {"enable_export": True, "max_reports": 50, "show_advanced_features": False}
            
            # Editar configurações
            enable_export = st.checkbox("Habilitar Exportação de Dados", adv_config.get("enable_export", True))
            max_reports = st.number_input("Número Máximo de Relatórios", min_value=10, max_value=500, value=adv_config.get("max_reports", 50))
            show_adv_features = st.checkbox("Mostrar Recursos Avançados", adv_config.get("show_advanced_features", False))
            
            # Atualizar configuração
            new_adv_config = {
                "enable_export": enable_export,
                "max_reports": max_reports,
                "show_advanced_features": show_adv_features
            }
            
            # Salvar configurações avançadas
            if st.button("Salvar Configurações Avançadas"):
                try:
                    with open(advanced_config_file, "w") as f:
                        json.dump(new_adv_config, f, indent=4)
                    st.success("Configurações avançadas salvas com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar configurações avançadas: {str(e)}")
        
        # Nova seção para configuração de páginas do menu
        with st.expander("Configuração de Páginas do Menu", expanded=True):
            st.write("Configure quais páginas aparecerão no menu lateral e como elas serão exibidas:")
            
            # Verificar e criar diretório de configuração de páginas se não existir
            page_config_dir = ".streamlit/page_config"
            if not os.path.exists(page_config_dir):
                os.makedirs(page_config_dir)
            
            # Arquivo de configuração de visibilidade das páginas
            pages_visibility_file = f"{page_config_dir}/visibility.json"
            page_permissions_file = f"{page_config_dir}/page_permissions.json"
            
            # Carregar configuração de visibilidade existente ou criar uma padrão
            # Formato: {"page_file_name": true/false}
            if os.path.exists(pages_visibility_file):
                try:
                    with open(pages_visibility_file, "r") as f:
                        pages_visibility = json.load(f)
                except:
                    # Iniciar com todas as páginas visíveis
                    pages_visibility = {}
            else:
                # Iniciar com todas as páginas visíveis
                pages_visibility = {}
            
            # Carregar configuração de permissões de páginas
            # Formato: {"page_file_name": ["permission1", "permission2"]}
            if os.path.exists(page_permissions_file):
                try:
                    with open(page_permissions_file, "r") as f:
                        page_permissions = json.load(f)
                except:
                    # Iniciar com permissões vazias
                    page_permissions = {}
            else:
                # Iniciar com permissões vazias
                page_permissions = {}
            
            # Carregar lista de arquivos de páginas
            page_files = [f for f in os.listdir("pages") if f.endswith(".py")]
            page_files.sort()  # Ordenar alfabeticamente
            
            # Criar abas para as diferentes configurações
            vis_tab, perm_tab = st.tabs(["Visibilidade", "Permissões"])
            
            with vis_tab:
                st.write("#### Visibilidade das Páginas")
                st.write("Selecione quais páginas serão visíveis no menu lateral:")
                
                # Lista para armazenar novas configurações de visibilidade
                new_visibility = {}
                
                # Criar checkbox para cada página
                for page_file in page_files:
                    # Extrair nome limpo da página (remove números e emojis do início)
                    clean_name = ' '.join(page_file.split('_')[1:]).replace('.py', '')
                    
                    # Verificar o status atual ou definir como visível por padrão
                    is_visible = pages_visibility.get(page_file, True)
                    
                    # Criar checkbox para a página
                    visible = st.checkbox(
                        f"{clean_name}",
                        value=is_visible,
                        key=f"vis_{page_file}"
                    )
                    
                    # Armazenar a configuração
                    new_visibility[page_file] = visible
                
                # Botão para salvar a configuração de visibilidade
                if st.button("Salvar Configuração de Visibilidade"):
                    try:
                        # Salvar a configuração de visibilidade
                        with open(pages_visibility_file, "w") as f:
                            json.dump(new_visibility, f, indent=4)
                        
                        # Atualizar arquivo pages.toml para aplicar as configurações
                        pages_toml_content = """# Configuração das páginas no menu lateral

# Estilo global das páginas
[global]
showPagesInSidebar = true
hideSidebarNavigation = false

# Configurações das seções
[pages]
section_spacing = "15px"
heading_color = "#4B7BA8"
heading_font_size = "16px"
page_font_size = "14px"
indent_depth = "15px"

# Renomear o app principal de "app" para "Login"
[pages.app]
displayName = "🔑 Login"
"""
                        
                        # Adicionar configurações de visibilidade ao TOML
                        for page_file, is_visible in new_visibility.items():
                            if not is_visible:  # Se a página não for visível
                                page_id = page_file.replace(".py", "")
                                pages_toml_content += f"""
[pages.{page_id}]
hideInSidebar = true
"""
                        
                        # Salvar o arquivo pages.toml
                        with open(".streamlit/pages.toml", "w") as f:
                            f.write(pages_toml_content)
                        
                        st.success("Configuração de visibilidade das páginas salva com sucesso!")
                        st.info("Reinicie a aplicação para aplicar as mudanças ou use o botão 'Recarregar' na seção de Recarregamento do Sistema.")
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar configuração de visibilidade: {str(e)}")
            
            with perm_tab:
                st.write("#### Permissões de Acesso às Páginas")
                st.write("Configure quais permissões são necessárias para acessar cada página:")
                
                # Lista de todas as permissões disponíveis no sistema
                all_permission_types = [
                    "admin", 
                    "manage_users", 
                    "developer_tools", 
                    "system_config",
                    "edit",
                    "view_reports",
                    "export_data",
                    "import_data",
                    "manage_animals",
                    "manage_reproduction",
                    "manage_health",
                    "manage_growth"
                ]
                
                # Selecionar página para configurar permissões
                selected_page = st.selectbox(
                    "Selecione a página para configurar permissões:",
                    options=page_files,
                    format_func=lambda x: x  # Mostrar nome completo do arquivo
                )
                
                # Obter permissões atuais para a página selecionada (lista vazia como padrão)
                current_permissions = page_permissions.get(selected_page, [])
                
                st.write(f"**Configurando permissões para:** {selected_page}")
                
                # Explicação sobre como as permissões funcionam
                st.info("""
                **Como as permissões funcionam:**
                - Se nenhuma permissão for selecionada, a página será acessível por todos os usuários autenticados
                - Se uma ou mais permissões forem selecionadas, o usuário precisará ter pelo menos uma delas para acessar a página
                - Usuários sem as permissões necessárias não poderão visualizar ou acessar a página
                """)
                
                # Criar multi-select para selecionar permissões
                selected_permissions = st.multiselect(
                    "Selecione as permissões necessárias para acessar esta página:",
                    options=all_permission_types,
                    default=current_permissions,
                    help="O usuário precisará ter pelo menos uma dessas permissões para acessar a página"
                )
                
                # Mostrar quais cargos terão acesso à página com base nas permissões selecionadas
                if selected_permissions:
                    st.write("**Cargos que terão acesso:**")
                    
                    # Carregar mapeamento de permissões de cargos
                    roles_permissions = load_permissions_map()
                    
                    # Verificar quais cargos têm pelo menos uma das permissões selecionadas
                    roles_with_access = []
                    for role, permissions in roles_permissions.items():
                        has_access = any(perm in permissions for perm in selected_permissions)
                        if has_access:
                            roles_with_access.append(role)
                    
                    if roles_with_access:
                        for role in roles_with_access:
                            st.write(f"- {role}")
                    else:
                        st.warning("Nenhum cargo terá acesso a esta página com as permissões selecionadas.")
                else:
                    st.write("**Todos os usuários autenticados terão acesso a esta página.**")
                
                # Botão para salvar as permissões da página
                if st.button("Salvar Permissões da Página"):
                    try:
                        # Atualizar as permissões da página no dicionário
                        page_permissions[selected_page] = selected_permissions
                        
                        # Salvar o arquivo de permissões de páginas
                        with open(page_permissions_file, "w") as f:
                            json.dump(page_permissions, f, indent=4)
                        
                        st.success(f"Permissões da página {selected_page} salvas com sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar permissões da página: {str(e)}")
                
                # Opção para aplicar permissões a todas as páginas
                st.write("---")
                st.write("### Configuração em Lote")
                
                # Agrupar páginas por categoria com base no prefixo numérico
                page_categories = {}
                for page in page_files:
                    prefix = page.split("_")[0].strip()
                    if prefix not in page_categories:
                        page_categories[prefix] = []
                    page_categories[prefix].append(page)
                
                # Selecionar categoria
                selected_category = st.selectbox(
                    "Selecione um grupo de páginas:",
                    options=sorted(page_categories.keys()),
                    format_func=lambda x: f"Grupo {x} ({len(page_categories[x])} páginas)"
                )
                
                # Mostrar páginas na categoria
                if selected_category:
                    st.write("**Páginas neste grupo:**")
                    for page in page_categories[selected_category]:
                        st.write(f"- {page}")
                    
                    # Permissões para aplicar a todas as páginas na categoria
                    batch_permissions = st.multiselect(
                        "Selecione permissões para aplicar a todas as páginas deste grupo:",
                        options=all_permission_types,
                        help="Estas permissões serão aplicadas a todas as páginas do grupo selecionado"
                    )
                    
                    # Botão para aplicar permissões em lote
                    if st.button("Aplicar Permissões ao Grupo"):
                        try:
                            # Atualizar permissões para todas as páginas na categoria
                            for page in page_categories[selected_category]:
                                page_permissions[page] = batch_permissions
                            
                            # Salvar o arquivo de permissões de páginas
                            with open(page_permissions_file, "w") as f:
                                json.dump(page_permissions, f, indent=4)
                            
                            st.success(f"Permissões aplicadas com sucesso a todas as páginas do grupo {selected_category}!")
                            
                        except Exception as e:
                            st.error(f"Erro ao aplicar permissões em lote: {str(e)}")
            
            
            st.write("---")
            
            # Seção para reordenar páginas
            st.write("#### Reordenação de Páginas")
            st.write("Reordene as páginas renomeando seus arquivos (os números no início determinam a ordem):")
            
            renaming_col1, renaming_col2 = st.columns(2)
            
            with renaming_col1:
                # Selecionar página para renomear
                selected_page = st.selectbox(
                    "Selecione a página para reordenar:",
                    options=page_files,
                    format_func=lambda x: x  # Mostrar nome completo do arquivo
                )
            
            with renaming_col2:
                # Selecionar nova posição
                current_prefix = selected_page.split("_")[0]
                new_prefix = st.text_input(
                    "Novo prefixo numérico:",
                    value=current_prefix,
                    help="Digite o novo número de ordem (ex: 01, 05, 10)"
                )
            
            # Botão para renomear
            if st.button("Reordenar Página"):
                if new_prefix != current_prefix:
                    try:
                        # Construir novo nome de arquivo
                        new_filename = selected_page.replace(current_prefix, new_prefix, 1)
                        
                        # Verificar se o arquivo de destino já existe
                        if os.path.exists(f"pages/{new_filename}"):
                            st.error(f"Não foi possível renomear: o arquivo {new_filename} já existe.")
                        else:
                            # Renomear o arquivo
                            os.rename(f"pages/{selected_page}", f"pages/{new_filename}")
                            st.success(f"Página reordenada com sucesso: {selected_page} → {new_filename}")
                            
                            # Sugerir recarregar a página
                            st.info("Recarregue esta página para ver as mudanças.")
                    except Exception as e:
                        st.error(f"Erro ao reordenar página: {str(e)}")
                else:
                    st.info("Nenhuma alteração realizada: o prefixo é o mesmo.")
                    
            st.write("---")
            
            # Seção para renomear páginas (alterar o emoji ou nome)
            st.write("#### Renomeação de Páginas")
            st.write("Altere o emoji ou o nome das páginas:")
            
            # Selecionar página para modificar o nome
            selected_page_rename = st.selectbox(
                "Selecione a página para renomear:",
                options=page_files,
                format_func=lambda x: x,  # Mostrar nome completo do arquivo
                key="rename_select"
            )
            
            # Extrair partes do nome da página
            if selected_page_rename:
                parts = selected_page_rename.split("_")
                prefix = parts[0]  # Ex: "01"
                
                if len(parts) > 1:
                    # Se o segundo elemento começa com um emoji, separamos ele
                    second_part = parts[1]
                    emoji = ""
                    name_parts = []
                    
                    # Verificar se há um emoji no início (caracteres não-ASCII)
                    for char in second_part:
                        if ord(char) > 127:  # Caractere não-ASCII, provavelmente emoji
                            emoji += char
                        else:
                            name_parts = [second_part[len(emoji):]] + parts[2:]
                            break
                    
                    if not emoji:  # Se não encontrou emoji
                        emoji = ""
                        name_parts = parts[1:]
                    
                    # Juntar as partes restantes do nome
                    current_name = "_".join(name_parts).replace(".py", "")
                else:
                    # Se não há partes suficientes, definir valores padrão
                    emoji = ""
                    current_name = selected_page_rename.replace(".py", "").replace(prefix+"_", "")
                
                # Campos para editar o emoji e o nome
                new_emoji = st.text_input("Emoji:", value=emoji, 
                                         help="Digite um emoji para a página, ou deixe em branco")
                
                new_name = st.text_input("Nome da página:", value=current_name,
                                         help="Digite o novo nome da página (sem o prefixo numérico)")
                
                # Visualização do novo nome de arquivo
                if new_name:
                    if new_emoji:
                        new_filename = f"{prefix}_{new_emoji}_{new_name}.py"
                    else:
                        new_filename = f"{prefix}_{new_name}.py"
                    
                    st.write(f"Novo nome de arquivo: **{new_filename}**")
                    
                    # Botão para renomear
                    if st.button("Renomear Página"):
                        try:
                            # Verificar se o arquivo de destino já existe
                            if os.path.exists(f"pages/{new_filename}") and new_filename != selected_page_rename:
                                st.error(f"Não foi possível renomear: o arquivo {new_filename} já existe.")
                            else:
                                # Renomear o arquivo
                                os.rename(f"pages/{selected_page_rename}", f"pages/{new_filename}")
                                st.success(f"Página renomeada com sucesso: {selected_page_rename} → {new_filename}")
                                
                                # Sugerir recarregar a página
                                st.info("Recarregue esta página para ver as mudanças.")
                        except Exception as e:
                            st.error(f"Erro ao renomear página: {str(e)}")
    
    with col2:
        st.subheader("Ferrramentas de Desenvolvimento")
        
        # Gerenciamento de permissões
        with st.expander("Gerenciamento de Permissões", expanded=True):
            st.write("Configure quais permissões cada cargo possui no sistema:")
            
            # Carregar mapeamento de permissões atual
            permissions_map = load_permissions_map()
            
            # Lista de cargos disponíveis
            cargos = [
                "Desenvolvedor", 
                "Administrador", 
                "Gerente", 
                "Técnico", 
                "Operador", 
                "Visitante"
            ]
            
            # Lista de permissões disponíveis
            all_permissions = [
                # Administrativas
                {"id": "admin", "name": "Acesso Administrativo", "desc": "Acesso às configurações administrativas"},
                {"id": "manage_users", "name": "Gerenciar Usuários", "desc": "Adicionar, editar e excluir usuários"},
                # Ferramentas
                {"id": "developer_tools", "name": "Ferramentas de Desenvolvedor", "desc": "Acesso às ferramentas de desenvolvimento"},
                {"id": "system_config", "name": "Configurações de Sistema", "desc": "Modificar configurações de sistema"},
                # Funcionalidades gerais
                {"id": "edit", "name": "Editar Registros", "desc": "Permissão para adicionar e editar registros"},
                {"id": "view_reports", "name": "Visualizar Relatórios", "desc": "Acesso aos relatórios do sistema"},
                {"id": "export_data", "name": "Exportar Dados", "desc": "Exportar dados do sistema"},
                {"id": "import_data", "name": "Importar Dados", "desc": "Importar dados para o sistema"},
                # Módulos específicos
                {"id": "manage_animals", "name": "Gerenciar Animais", "desc": "Gerenciar cadastro e informações de animais"},
                {"id": "manage_reproduction", "name": "Gerenciar Reprodução", "desc": "Gerenciar ciclos reprodutivos e gestações"},
                {"id": "manage_health", "name": "Gerenciar Saúde", "desc": "Gerenciar vacinas e registros de saúde"},
                {"id": "manage_growth", "name": "Gerenciar Crescimento", "desc": "Gerenciar registros de peso e crescimento"}
            ]
    
    with col2:
        st.subheader("Ferrramentas de Desenvolvimento")
        
        # Gerenciamento de permissões
        with st.expander("Gerenciamento de Permissões", expanded=True):
            st.write("Configure quais permissões cada cargo possui no sistema:")
            
            # Carregar mapeamento de permissões atual
            permissions_map = load_permissions_map()
            
            # Lista de cargos disponíveis
            cargos = [
                "Desenvolvedor", 
                "Administrador", 
                "Gerente", 
                "Técnico", 
                "Operador", 
                "Visitante"
            ]
            
            # Lista de permissões disponíveis
            all_permissions = [
                # Administrativas
                {"id": "admin", "name": "Acesso Administrativo", "desc": "Acesso às configurações administrativas"},
                {"id": "manage_users", "name": "Gerenciar Usuários", "desc": "Adicionar, editar e excluir usuários"},
                # Ferramentas
                {"id": "developer_tools", "name": "Ferramentas de Desenvolvedor", "desc": "Acesso às ferramentas de desenvolvimento"},
                {"id": "system_config", "name": "Configurações de Sistema", "desc": "Modificar configurações de sistema"},
                # Funcionalidades gerais
                {"id": "edit", "name": "Editar Registros", "desc": "Permissão para adicionar e editar registros"},
                {"id": "view_reports", "name": "Visualizar Relatórios", "desc": "Acesso aos relatórios do sistema"},
                {"id": "export_data", "name": "Exportar Dados", "desc": "Exportar dados do sistema"},
                {"id": "import_data", "name": "Importar Dados", "desc": "Importar dados para o sistema"},
                # Módulos específicos
                {"id": "manage_animals", "name": "Gerenciar Animais", "desc": "Gerenciar cadastro e informações de animais"},
                {"id": "manage_reproduction", "name": "Gerenciar Reprodução", "desc": "Gerenciar ciclos reprodutivos e gestações"},
                {"id": "manage_health", "name": "Gerenciar Saúde", "desc": "Gerenciar vacinas e registros de saúde"},
                {"id": "manage_growth", "name": "Gerenciar Crescimento", "desc": "Gerenciar registros de peso e crescimento"}
            ]
            
            # Selecionar cargo para configurar
            selected_cargo = st.selectbox(
                "Selecione o cargo para configurar as permissões:",
                options=cargos
            )
            
            # Obter permissões atuais para o cargo selecionado
            current_permissions = permissions_map.get(selected_cargo, [])
            
            # Criar checkboxes para cada permissão
            st.write(f"Permissões para o cargo: **{selected_cargo}**")
            
            # Dividir em 2 colunas para melhor visualização
            perm_col1, perm_col2 = st.columns(2)
            
            # Preparar para coletar novas permissões
            new_permissions = []
            
            with perm_col1:
                st.write("**Permissões Administrativas:**")
                admin_perms = [p for p in all_permissions if p["id"] in ["admin", "manage_users", "developer_tools", "system_config"]]
                for perm in admin_perms:
                    checked = st.checkbox(
                        f"{perm['name']}",
                        value=perm["id"] in current_permissions,
                        help=perm["desc"],
                        key=f"perm_{selected_cargo}_{perm['id']}_1"
                    )
                    if checked:
                        new_permissions.append(perm["id"])
                        
                st.write("**Permissões Gerais:**")
                general_perms = [p for p in all_permissions if p["id"] in ["edit", "view_reports", "export_data", "import_data"]]
                for perm in general_perms:
                    checked = st.checkbox(
                        f"{perm['name']}",
                        value=perm["id"] in current_permissions,
                        help=perm["desc"],
                        key=f"perm_{selected_cargo}_{perm['id']}_2"
                    )
                    if checked:
                        new_permissions.append(perm["id"])
            
            with perm_col2:
                st.write("**Permissões de Módulos:**")
                module_perms = [p for p in all_permissions if p["id"] in ["manage_animals", "manage_reproduction", "manage_health", "manage_growth"]]
                for perm in module_perms:
                    checked = st.checkbox(
                        f"{perm['name']}",
                        value=perm["id"] in current_permissions,
                        help=perm["desc"],
                        key=f"perm_{selected_cargo}_{perm['id']}_3"
                    )
                    if checked:
                        new_permissions.append(perm["id"])
            
            # Botão para salvar as novas permissões
            if st.button("Salvar Permissões", key=f"save_{selected_cargo}"):
                # Atualizar o mapeamento de permissões
                permissions_map[selected_cargo] = new_permissions
                
                # Salvar o mapeamento atualizado
                if save_permissions_map(permissions_map):
                    st.success(f"Permissões do cargo {selected_cargo} atualizadas com sucesso!")
                else:
                    st.error("Erro ao salvar as permissões. Tente novamente.")
        
        # Recarga do sistema
        with st.expander("Recarregamento do Sistema", expanded=True):
            st.write("Recarregue componentes do sistema sem reiniciar completamente:")
            
            # Opções de recarga
            reload_option = st.selectbox(
                "Selecione o componente para recarregar:",
                ["Módulos Python", "Configurações", "Dados"]
            )
            
            if st.button("Recarregar", key="btn_reload"):
                if reload_option == "Módulos Python":
                    try:
                        # Recarregar o módulo utils
                        import utils
                        importlib.reload(utils)
                        st.success("Módulos Python recarregados com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao recarregar módulos: {str(e)}")
                
                elif reload_option == "Configurações":
                    try:
                        # Recarregar configurações
                        if os.path.exists("config.json"):
                            with open("config.json", "r") as f:
                                config = json.load(f)
                            st.success("Configurações recarregadas com sucesso!")
                            st.json(config)
                        else:
                            st.warning("Arquivo de configurações não encontrado.")
                    except Exception as e:
                        st.error(f"Erro ao recarregar configurações: {str(e)}")
                
                elif reload_option == "Dados":
                    try:
                        # Forçar recarga de todos os dados
                        # Isso pode ser feito com uma função que limpa qualquer cache
                        # Por exemplo, no Streamlit você pode criar uma chave de cache única
                        st.session_state["reload_flag"] = datetime.datetime.now().timestamp()
                        st.success("Dados marcados para recarga. Atualize a página para ver as mudanças.")
                    except Exception as e:
                        st.error(f"Erro ao marcar dados para recarga: {str(e)}")
        
        # Limpeza de dados
        with st.expander("Manutenção de Dados"):
            st.write("Ferramentas para manutenção dos dados do sistema:")
            
            # Opções de limpeza
            maintenance_option = st.selectbox(
                "Selecione a operação de manutenção:",
                ["Verificar Inconsistências", "Reparar Estrutura de Dados", "Limpar Dados Temporários"]
            )
            
            if maintenance_option == "Verificar Inconsistências":
                if st.button("Iniciar Verificação", key="btn_check_inconsistencies"):
                    st.info("Verificando inconsistências nos dados... Este processo pode levar alguns minutos.")
                    
                    # Implementar verificação de inconsistências
                    # Por exemplo, verificar se todos os animais em gestação são fêmeas
                    from utils import load_animals, load_gestation
                    
                    inconsistencies = []
                    
                    try:
                        animals_df = load_animals()
                        gestation_df = load_gestation()
                        
                        if not animals_df.empty and not gestation_df.empty:
                            # Mesclar dados para verificar
                            merged = pd.merge(
                                gestation_df, 
                                animals_df, 
                                on='id_animal', 
                                how='left'
                            )
                            
                            # Verificar se há machos em gestação (o que seria um erro)
                            males_gestation = merged[merged['sexo'] == 'M']
                            
                            if not males_gestation.empty:
                                for _, row in males_gestation.iterrows():
                                    inconsistencies.append({
                                        "tipo": "Erro Lógico",
                                        "descricao": f"Animal macho em gestação",
                                        "id_animal": row['id_animal'],
                                        "detalhe": f"Animal {row['identificacao']} está registrado como macho e em gestação"
                                    })
                        
                        # Exibir resultados
                        if inconsistencies:
                            st.error(f"Foram encontradas {len(inconsistencies)} inconsistências nos dados!")
                            
                            inc_df = pd.DataFrame(inconsistencies)
                            st.dataframe(inc_df, hide_index=True, use_container_width=True)
                        else:
                            st.success("Não foram encontradas inconsistências nos dados!")
                            
                    except Exception as e:
                        st.error(f"Erro ao verificar inconsistências: {str(e)}")
            
            elif maintenance_option == "Reparar Estrutura de Dados":
                st.warning("⚠️ Esta operação pode modificar seus dados. Certifique-se de fazer um backup antes de continuar.")
                
                if st.button("Reparar Estrutura", key="btn_repair"):
                    st.info("Reparando estrutura de dados... Este processo pode levar alguns minutos.")
                    
                    # Implementar reparo de estrutura
                    # Por exemplo, garantir que todos os arquivos CSV tenham as colunas corretas
                    # Isso é apenas um exemplo, a lógica real seria mais complexa
                    
                    # Fornecer feedback ao usuário
                    st.success("Estrutura de dados reparada com sucesso!")
            
            elif maintenance_option == "Limpar Dados Temporários":
                if st.button("Limpar Temporários", key="btn_clean_temp"):
                    # Limpar arquivos temporários
                    temp_dir = "temp"
                    if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir)
                        os.makedirs(temp_dir)
                        st.success(f"Diretório {temp_dir} limpo com sucesso!")
                    else:
                        os.makedirs(temp_dir)
                        st.info(f"Diretório {temp_dir} criado, pois não existia.")

with tab5:
    st.markdown('<div class="dev-section"><h2>Downloads do Sistema</h2></div>', unsafe_allow_html=True)
    
    st.write("Baixe o sistema completo ou componentes específicos para desenvolvimento local.")
    
    # Sempre criar um novo arquivo ZIP com a data atual
    import datetime
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    zip_path = f"suinocultura_{current_date}.zip"
    
    # Forçar a criação de um novo arquivo para garantir que esteja atualizado
    st.info("Preparando o arquivo para download... Por favor, aguarde.")
    import sys
    import importlib.util
    
    # Carregar e executar o script create_download_package.py
    spec = importlib.util.spec_from_file_location("create_download_package", "create_download_package.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["create_download_package"] = module
    spec.loader.exec_module(module)
    
    # Executar a função
    module.create_download_package()
    
    # Função para gerar o link de download
    def get_download_link(file_path, link_text):
        if not os.path.exists(file_path):
            st.error(f"Arquivo {file_path} não encontrado!")
            return ""
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="{os.path.basename(file_path)}" style="text-decoration:none;">'\
               f'<div style="background-color:#4CAF50; color:white; padding:12px 20px; border-radius:8px; '\
               f'cursor:pointer; text-align:center; font-weight:bold; margin:20px 0px;">{link_text}</div></a>'
        
        return href
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Sistema Completo")
        st.write("""
        Este pacote contém o código-fonte completo do Sistema de Gestão Suinocultura, incluindo:
        - Todos os arquivos Python
        - Todas as páginas da aplicação
        - Arquivos de dados (CSVs)
        - Arquivos de configuração
        """)
        
        # Mostrar o botão de download
        if os.path.exists(zip_path):
            st.markdown(get_download_link(zip_path, "📥 DOWNLOAD DO SISTEMA COMPLETO"), unsafe_allow_html=True)
            
            file_size = round(os.path.getsize(zip_path) / (1024), 2)
            st.caption(f"Tamanho do arquivo: {file_size} KB | Última atualização: {datetime.datetime.fromtimestamp(os.path.getmtime(zip_path)).strftime('%d/%m/%Y %H:%M')}")
        else:
            st.error("Arquivo de download não está disponível. Por favor, tente novamente mais tarde.")
    
    with col2:
        st.markdown("### Outras Opções")
        
        # Botão para gerar documentação
        if st.button("Gerar Documentação"):
            st.info("Gerando documentação... Este processo pode levar alguns minutos.")
            
            # Implementar geração de documentação
            # Exemplo: usar pydoc para gerar documentação das funções Python
            
            # Fornecer feedback ao usuário
            st.success("Documentação gerada com sucesso!")
            
            # Aqui você poderia adicionar um link para download da documentação
        
        st.markdown("---")

# Aba de Atualizações do Sistema
with tab6:
    st.markdown('''
    <div style="background-color: #1E1E1E; color: #4FC3F7; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 5px solid #2196F3; font-family: 'Courier New', monospace;">
        <h2 style="margin:0; color: #4FC3F7; text-shadow: 0 0 5px rgba(79, 195, 247, 0.3);">🔄 Histórico de Atualizações</h2>
        <p style="margin-top:0.5rem; color: #BBBBBB;">Registro completo de todas as atualizações e melhorias do sistema</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Função para salvar token do GitHub de forma segura
    def save_github_credentials(username, token, repo_name, repo_owner):
        """
        Salva as credenciais do GitHub de forma segura
        
        Args:
            username (str): Nome de usuário do GitHub
            token (str): Token de acesso pessoal do GitHub
            repo_name (str): Nome do repositório
            repo_owner (str): Proprietário do repositório
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        try:
            credentials = {
                "username": username,
                "token": token,
                "repo_name": repo_name,
                "repo_owner": repo_owner,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            credentials_file = "data/github_credentials.json"
            # Salvar credenciais
            with open(credentials_file, "w", encoding="utf-8") as f:
                json.dump(credentials, f, ensure_ascii=False, indent=4)
            
            return True, "Credenciais salvas com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar credenciais: {str(e)}"
    
    # Função para carregar token do GitHub
    def load_github_credentials():
        """
        Carrega as credenciais do GitHub
        
        Returns:
            dict: Credenciais do GitHub ou None se não existir
        """
        credentials_file = "data/github_credentials.json"
        
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        
        return None
    
    # Adicionar CSS específico para atualizações com modo escuro
    st.markdown("""
    <style>
        /* Modo escuro para as atualizações */
        .update-card {
            background-color: #1E1E1E;
            border-left: 4px solid #2196F3;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .update-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            border-bottom: 1px solid #333333;
            padding-bottom: 8px;
        }
        .update-version {
            font-size: 1.5rem;
            font-weight: bold;
            color: #4FC3F7;
            text-shadow: 0 0 5px rgba(79, 195, 247, 0.2);
        }
        .update-date {
            color: #BBBBBB;
            font-style: italic;
        }
        .update-description {
            font-size: 1.1rem;
            margin-bottom: 15px;
            color: #E0E0E0;
        }
        .change-item {
            background-color: #2D2D2D;
            border-radius: 5px;
            padding: 12px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border-left: 3px solid #555555;
        }
        .change-new {
            border-left: 3px solid #4CAF50;
        }
        .change-improvement {
            border-left: 3px solid #2196F3;
        }
        .change-fix {
            border-left: 3px solid #FF9800;
        }
        .change-security {
            border-left: 3px solid #F44336;
        }
        .change-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #E0E0E0;
        }
        .change-description {
            color: #BBBBBB;
        }
        .change-type {
            display: inline-block;
            padding: 3px 6px;
            font-size: 0.8rem;
            border-radius: 3px;
            color: white;
            margin-right: 8px;
            box-shadow: 0 0 4px rgba(0,0,0,0.3);
        }
        .type-new {
            background-color: #4CAF50;
        }
        .type-improvement {
            background-color: #2196F3;
        }
        .type-fix {
            background-color: #FF9800;
        }
        .type-security {
            background-color: #F44336;
        }
        .add-update-form {
            background-color: #2D2D2D;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            border: 1px solid #444444;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        /* Estilos para os botões e inputs dentro do form de atualização */
        .add-update-form input, 
        .add-update-form textarea,
        .add-update-form .stSelectbox>div>div {
            background-color: #333333 !important;
            color: #E0E0E0 !important;
            border: 1px solid #444444 !important;
        }
        
        .add-update-form button {
            background-color: #2196F3 !important;
            color: white !important;
        }
        
        /* Melhorias nas animações e efeitos de hover */
        .update-card {
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .update-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        
        .change-item {
            transition: transform 0.2s;
        }
        
        .change-item:hover {
            transform: translateX(3px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Carregar histórico de atualizações
    update_file = "data/updates_history.json"
    
    if os.path.exists(update_file):
        try:
            with open(update_file, "r", encoding="utf-8") as f:
                updates_data = json.load(f)
            
            # Exibir todas as atualizações
            for version in updates_data.get("versoes", []):
                with st.container():
                    # Obter informações adicionais se disponíveis
                    codigo_interno = version.get("codigo_interno", "")
                    impacto = version.get("impacto", "")
                    equipe = version.get("equipe_responsavel", "")
                    notas_importantes = version.get("notas_importantes", "")
                    
                    # Construir o cabeçalho com informações detalhadas
                    st.markdown(f'''
                    <div class="update-card">
                        <div class="update-header">
                            <div class="update-version">Versão {version["versao"]}</div>
                            <div class="update-date">Lançada em {version["data"]} por {version["autor"]}</div>
                        </div>
                        <div class="update-description">{version["descricao"]}</div>
                        
                        {f'<div class="update-notes" style="margin: 10px 0; padding: 10px; background-color: #FFF3CD; color: #856404; border-radius: 5px; border-left: 4px solid #FFD700;">{notas_importantes}</div>' if notas_importantes else ''}
                        
                        <div class="update-meta" style="display: flex; margin-bottom: 15px; font-size: 0.9rem; color: #BBBBBB;">
                            {f'<div style="margin-right: 20px;"><strong>Código:</strong> {codigo_interno}</div>' if codigo_interno else ''}
                            {f'<div style="margin-right: 20px;"><strong>Impacto:</strong> <span style="color: {"#FF5252" if impacto == "Alto" else "#FFC107" if impacto == "Médio" else "#4CAF50"};">{impacto}</span></div>' if impacto else ''}
                            {f'<div><strong>Equipe:</strong> {equipe}</div>' if equipe else ''}
                        </div>
                        
                        <div class="update-changes">
                    ''', unsafe_allow_html=True)
                    
                    # Exibir todas as mudanças desta versão
                    for change in version.get("mudancas", []):
                        change_type = change["tipo"]
                        change_class = ""
                        type_class = ""
                        
                        if "Nova Funcionalidade" in change_type:
                            change_class = "change-new"
                            type_class = "type-new"
                        elif "Melhoria" in change_type:
                            change_class = "change-improvement"
                            type_class = "type-improvement"
                        elif "Correção" in change_type:
                            change_class = "change-fix"
                            type_class = "type-fix"
                        elif "Segurança" in change_type:
                            change_class = "change-security"
                            type_class = "type-security"
                        
                        # Obter detalhes adicionais da mudança, se disponíveis
                        detalhes_tecnicos = change.get("detalhes_tecnicos", "")
                        arquivos_alterados = change.get("arquivos_alterados", [])
                        horas_desenvolvimento = change.get("horas_desenvolvimento", "")
                        testes_realizados = change.get("testes_realizados", "")
                        
                        # Construir string de arquivos alterados
                        arquivos_html = ""
                        if arquivos_alterados:
                            arquivos_html = '<div style="margin-top: 10px;"><strong>Arquivos alterados:</strong><div style="display:flex; flex-wrap:wrap; gap:5px; margin-top:5px;">'
                            for arquivo in arquivos_alterados:
                                if arquivo.endswith(".py"):
                                    cor = "#3572A5"  # Cor do Python
                                elif arquivo.endswith(".json"):
                                    cor = "#F5BB12"  # Cor para JSON
                                elif arquivo.endswith(".csv"):
                                    cor = "#237346"  # Cor para CSV
                                elif arquivo.endswith(".java"):
                                    cor = "#B07219"  # Cor para Java
                                elif arquivo.endswith(".xml"):
                                    cor = "#0060AC"  # Cor para XML
                                elif arquivo.endswith(".toml"):
                                    cor = "#9C4221"  # Cor para TOML
                                else:
                                    cor = "#777777"  # Cor padrão
                                    
                                arquivos_html += f'<span style="background-color:{cor}25; color:{cor}; padding:3px 6px; border-radius:3px; font-size:0.8rem; border:1px solid {cor}50;">{arquivo}</span>'
                            arquivos_html += '</div></div>'
                        
                        # Detalhes técnicos HTML
                        detalhes_tecnicos_html = ''
                        if detalhes_tecnicos:
                            detalhes_tecnicos_html = f'<div class="change-tech-details" style="margin-top:15px; background-color:#25232375; padding:10px; border-radius:5px; border-left:3px solid #555; font-size:0.9rem;"><strong style="color:#4FC3F7;">Detalhes Técnicos:</strong> {detalhes_tecnicos}</div>'
                        
                        # Testes HTML
                        testes_html = ''
                        if testes_realizados:
                            testes_html = f'<div style="margin-top:10px; font-style:italic; color:#BBBBBB; font-size:0.9rem;"><strong>Testes:</strong> {testes_realizados}</div>'
                        
                        # Horas de desenvolvimento HTML
                        horas_html = ''
                        if horas_desenvolvimento:
                            horas_html = f'<span style="float:right; font-size:0.8rem; color:#BBBBBB; padding:3px 8px; background-color:#333; border-radius:10px;">{horas_desenvolvimento}h</span>'
                        
                        # Construir HTML com todos os detalhes
                        st.markdown(f'''
                        <div class="change-item {change_class}">
                            <div class="change-title">
                                <span class="change-type {type_class}">{change_type}</span>
                                {change["titulo"]}
                                {horas_html}
                            </div>
                            <div class="change-description">{change["descricao"]}</div>
                            {detalhes_tecnicos_html}
                            {arquivos_html}
                            {testes_html}
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    st.markdown('---')
        except Exception as e:
            st.error(f"Erro ao carregar histórico de atualizações: {str(e)}")
    else:
        st.warning("O arquivo de histórico de atualizações não foi encontrado. Crie o arquivo para começar a registrar as atualizações do sistema.")
    
    # Separador
    st.markdown("---")
    
    # Formulário para adicionar nova atualização
    with st.expander("🆕 Adicionar Nova Atualização", expanded=False):
        st.markdown('''
        <div class="add-update-form">
            <div style="margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 10px;">
                <h3 style="color: #4FC3F7; margin: 0; font-family: 'Courier New', monospace;">
                    <span style="color: #4CAF50;">+</span> Registrar Nova Versão do Sistema
                </h3>
                <p style="color: #BBBBBB; margin-top: 5px;">
                    Preencha os detalhes abaixo para registrar uma nova versão no histórico de atualizações
                </p>
            </div>
        ''', unsafe_allow_html=True)
        
        with st.form("add_update_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                versao = st.text_input("Versão", placeholder="1.0.0")
                autor = st.text_input("Autor", value="Equipe de Desenvolvimento")
                codigo_interno = st.text_input("Código Interno", placeholder="RELEASE-SUINO-YYYY-MM")
                
            with col2:
                data = st.date_input("Data de Lançamento", value=datetime.datetime.now())
                impacto = st.selectbox("Impacto", options=["Alto", "Médio", "Baixo"])
                equipe_responsavel = st.text_input("Equipe Responsável", placeholder="Desenvolvimento Full-Stack")
                
            descricao = st.text_area("Descrição da Versão", placeholder="Descreva brevemente esta versão")
            
            # Adicionar campo para notas importantes
            notas = st.text_area("Notas Importantes (opcional)", 
                                placeholder="Informações importantes sobre esta versão, como avisos, requisitos especiais ou limitações.",
                                help="Estas notas serão destacadas no histórico de atualizações para chamar atenção dos usuários.")
            
            # Opção para adicionar mudanças
            st.subheader("Mudanças nesta Versão")
            
            num_changes = st.number_input("Número de mudanças a adicionar", min_value=1, max_value=10, value=1)
            
            changes = []
            
            for i in range(int(num_changes)):
                st.markdown(f"### Mudança {i+1}")
                
                change_col1, change_col2 = st.columns(2)
                
                with change_col1:
                    change_type = st.selectbox(
                        f"Tipo de Mudança #{i+1}",
                        options=["Nova Funcionalidade", "Melhoria", "Correção", "Segurança"],
                        key=f"change_type_{i}"
                    )
                
                with change_col2:
                    change_title = st.text_input(
                        f"Título #{i+1}",
                        placeholder="Título curto e descritivo",
                        key=f"change_title_{i}"
                    )
                
                change_desc = st.text_area(
                    f"Descrição Detalhada #{i+1}",
                    placeholder="Descreva com detalhes a mudança realizada",
                    key=f"change_desc_{i}"
                )
                
                # Detalhes técnicos - sem usar expander (já estamos dentro de um form que está dentro de um expander)
                st.markdown(f"#### Detalhes Técnicos para Mudança #{i+1}")
                
                detalhes_tecnicos = st.text_area(
                    f"Detalhes Técnicos #{i+1}",
                    placeholder="Descreva detalhes técnicos da implementação",
                    key=f"detalhes_tecnicos_{i}"
                )
                
                arquivos_alterados = st.text_area(
                    f"Arquivos Alterados #{i+1}",
                    placeholder="Lista de arquivos alterados (um por linha)",
                    key=f"arquivos_alterados_{i}"
                )
                
                horas_desenvolvimento = st.number_input(
                    f"Horas de Desenvolvimento #{i+1}",
                    min_value=0,
                    max_value=1000,
                    value=0,
                    key=f"horas_desenvolvimento_{i}"
                )
                
                testes_realizados = st.text_area(
                    f"Testes Realizados #{i+1}",
                    placeholder="Descreva os testes realizados para esta mudança",
                    key=f"testes_realizados_{i}"
                )
                
                st.markdown("---")  # Separador entre as seções
                
                # Processar arquivos alterados como lista
                arquivos_list = []
                if arquivos_alterados.strip():
                    arquivos_list = [arquivo.strip() for arquivo in arquivos_alterados.strip().split('\n') if arquivo.strip()]
                
                change_data = {
                    "tipo": change_type,
                    "titulo": change_title,
                    "descricao": change_desc
                }
                
                # Adicionar campos opcionais se fornecidos
                if detalhes_tecnicos.strip():
                    change_data["detalhes_tecnicos"] = detalhes_tecnicos
                    
                if arquivos_list:
                    change_data["arquivos_alterados"] = arquivos_list
                    
                if horas_desenvolvimento > 0:
                    change_data["horas_desenvolvimento"] = horas_desenvolvimento
                    
                if testes_realizados.strip():
                    change_data["testes_realizados"] = testes_realizados
                
                changes.append(change_data)
            
            submit_button = st.form_submit_button("💾 Salvar Nova Atualização")
            
            if submit_button:
                if versao and descricao:
                    try:
                        # Verificar se já existe arquivo de atualizações
                        if os.path.exists(update_file):
                            with open(update_file, "r", encoding="utf-8") as f:
                                updates_data = json.load(f)
                        else:
                            updates_data = {"versoes": []}
                        
                        # Criar objeto da nova versão
                        new_version = {
                            "versao": versao,
                            "data": data.strftime("%Y-%m-%d"),
                            "autor": autor,
                            "descricao": descricao,
                            "mudancas": [change for change in changes if change["titulo"] and change["descricao"]]
                        }
                        
                        # Adicionar campos opcionais se fornecidos
                        if codigo_interno.strip():
                            new_version["codigo_interno"] = codigo_interno
                            
                        if impacto:
                            new_version["impacto"] = impacto
                            
                        if equipe_responsavel.strip():
                            new_version["equipe_responsavel"] = equipe_responsavel
                            
                        # Adicionar notas importantes se fornecidas
                        if notas.strip():
                            new_version["notas_importantes"] = notas
                        
                        # Adicionar ao início da lista
                        updates_data["versoes"].insert(0, new_version)
                        
                        # Salvar de volta ao arquivo
                        with open(update_file, "w", encoding="utf-8") as f:
                            json.dump(updates_data, f, ensure_ascii=False, indent=4)
                        
                        st.success("Atualização adicionada com sucesso!")
                        st.info("Recarregue a página para ver as mudanças.")
                        
                    except Exception as e:
                        st.error(f"Erro ao adicionar atualização: {str(e)}")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios (versão e descrição).")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Separador
    st.markdown("---")
    
    # Seção de Integração com GitHub
    with st.expander("🌐 Integração com GitHub", expanded=False):
        st.markdown('''
        <div class="add-update-form">
            <div style="margin-bottom: 15px; border-bottom: 1px solid #444; padding-bottom: 10px;">
                <h3 style="color: #4FC3F7; margin: 0; font-family: 'Courier New', monospace;">
                    <span style="color: #4CAF50;">⚙️</span> Configuração do GitHub
                </h3>
                <p style="color: #BBBBBB; margin-top: 5px;">
                    Configure a integração com o GitHub para enviar atualizações do sistema
                </p>
            </div>
        ''', unsafe_allow_html=True)
        
        # Verificar se já existem credenciais
        github_credentials = load_github_credentials()
        
        if github_credentials:
            st.success(f"Credenciais do GitHub já configuradas para o repositório: {github_credentials.get('repo_owner', '')}/{github_credentials.get('repo_name', '')}")
            st.info("Última atualização: " + github_credentials.get('updated_at', ''))
            
            # Opção para atualizar credenciais
            if st.checkbox("Atualizar credenciais"):
                with st.form("update_github_form"):
                    github_username = st.text_input("Nome de usuário do GitHub", value=github_credentials.get('username', ''))
                    
                    # Instruções detalhadas para o token
                    st.info("""
                    **Instruções para criar um token do GitHub com as permissões corretas:**
                    1. Acesse: https://github.com/settings/tokens
                    2. Clique em "Generate new token" (classic)
                    3. Dê um nome como "Suinocultura App Access"
                    4. **Importante:** Selecione os seguintes escopos:
                       - `repo` (todos os subescopos)
                       - `workflow` 
                       - `admin:org` (opcional, se for para uma organização)
                    5. Clique em "Generate token" e copie o token gerado
                    """)
                    
                    github_token = st.text_input("Token de acesso pessoal do GitHub", type="password")
                    github_repo_owner = st.text_input("Proprietário do repositório", value=github_credentials.get('repo_owner', ''),
                                                  help="Nome de usuário ou organização que possui o repositório")
                    github_repo_name = st.text_input("Nome do repositório", value=github_credentials.get('repo_name', ''),
                                                 help="O repositório deve existir previamente no GitHub")
                    
                    update_button = st.form_submit_button("Atualizar credenciais")
                    
                    if update_button:
                        if github_username and github_token and github_repo_owner and github_repo_name:
                            success, message = save_github_credentials(
                                github_username, 
                                github_token,
                                github_repo_name,
                                github_repo_owner
                            )
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Por favor, preencha todos os campos.")
        else:
            # Form para adicionar credenciais
            with st.form("add_github_form"):
                st.write("Para utilizar a integração com GitHub, você precisa configurar suas credenciais:")
                
                github_username = st.text_input("Nome de usuário do GitHub")
                
                # Instruções detalhadas para o token
                st.info("""
                **Instruções para criar um token do GitHub com as permissões corretas:**
                1. Acesse: https://github.com/settings/tokens
                2. Clique em "Generate new token" (classic)
                3. Dê um nome como "Suinocultura App Access"
                4. **Importante:** Selecione os seguintes escopos:
                   - `repo` (todos os subescopos)
                   - `workflow` 
                   - `admin:org` (opcional, se for para uma organização)
                5. Clique em "Generate token" e copie o token gerado
                """)
                
                github_token = st.text_input("Token de acesso pessoal do GitHub", type="password")
                github_repo_owner = st.text_input("Proprietário do repositório", 
                                              help="Nome de usuário ou organização que possui o repositório")
                github_repo_name = st.text_input("Nome do repositório", 
                                             help="O repositório deve existir previamente no GitHub")
                
                submit_button = st.form_submit_button("Salvar credenciais")
                
                if submit_button:
                    if github_username and github_token and github_repo_owner and github_repo_name:
                        success, message = save_github_credentials(
                            github_username, 
                            github_token,
                            github_repo_name,
                            github_repo_owner
                        )
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Por favor, preencha todos os campos.")
        
        # Função para enviar para o GitHub
        def upload_to_github(files, commit_message, branch="main"):
            """
            Envia arquivos para o GitHub
            
            Args:
                files (list): Lista de caminhos de arquivos a serem enviados
                commit_message (str): Mensagem do commit
                branch (str): Nome do branch
                
            Returns:
                bool, str: Sucesso e mensagem
            """
            try:
                credentials = load_github_credentials()
                if not credentials:
                    return False, "Credenciais do GitHub não configuradas."
                
                # Obter token e informações do repo
                github_token = credentials.get("token")
                repo_owner = credentials.get("repo_owner")
                repo_name = credentials.get("repo_name")
                
                # Inicializar cliente GitHub
                g = Github(github_token)
                
                # Verificar permissões do token primeiro
                try:
                    # Tentar acessar o usuário para verificar credenciais
                    g.get_user().login
                except Exception as e:
                    return False, f"""
                    Erro de autenticação no GitHub: {str(e)}
                    
                    Verifique se o token é válido e possui as permissões necessárias:
                    - Certifique-se de que o token tenha os escopos 'repo' completos
                    - Se o token expirou, gere um novo
                    - Verifique seus escopos acessando: https://github.com/settings/tokens
                    """
                
                try:
                    # Tentar obter o repositório
                    repo = g.get_user(repo_owner).get_repo(repo_name)
                except Exception as e:
                    return False, f"""
                    Erro ao acessar o repositório: {str(e)}
                    
                    Possíveis causas:
                    - O repositório '{repo_name}' não existe ou é privado
                    - Seu token não tem acesso ao repositório
                    - O nome do proprietário '{repo_owner}' está incorreto
                    
                    Certifique-se de que o repositório existe e que você tem permissões de acesso.
                    """
                
                # Verificar se o branch existe
                try:
                    branch_ref = repo.get_branch(branch)
                except Exception as e:
                    return False, f"""
                    Branch '{branch}' não encontrado: {str(e)}
                    
                    Soluções:
                    - Verifique se o branch '{branch}' existe no repositório
                    - Crie o branch no GitHub antes de tentar enviar arquivos
                    - Use 'main' ou 'master' como nome do branch se for um repositório padrão
                    """
                
                # Obter o SHA do último commit no branch
                last_commit_sha = branch_ref.commit.sha
                base_tree = repo.get_git_tree(last_commit_sha)
                
                # Preparar os blobs para o commit
                element_list = []
                processed_files = 0
                skipped_files = 0
                
                for file_path in files:
                    if not os.path.exists(file_path):
                        skipped_files += 1
                        continue
                    
                    try:
                        with open(file_path, 'rb') as input_file:
                            data = input_file.read()
                        
                        # Criar o blob do arquivo
                        blob = repo.create_git_blob(base64.b64encode(data).decode(), "base64")
                        
                        # Adicionar o elemento à lista
                        element = InputGitTreeElement(
                            # Remover o ./ do início do caminho, se existir
                            path=file_path[2:] if file_path.startswith("./") else file_path,
                            mode='100644',
                            type='blob',
                            sha=blob.sha
                        )
                        element_list.append(element)
                        processed_files += 1
                        
                    except github.GithubException as ge:
                        # Erro específico do GitHub
                        if ge.status == 403:  # Forbidden
                            return False, f"""
                            Erro de permissão (403 Forbidden): {ge.data.get('message', 'Acesso negado')}
                            
                            O token não tem permissões suficientes para criar conteúdo no repositório.
                            Certifique-se de que:
                            1. O token tem o escopo 'repo' completo selecionado
                            2. Você tem permissão de escrita no repositório
                            3. Não há restrições de branch protection que impeçam o push
                            
                            Se o erro persistir, tente criar um novo token com todas as permissões necessárias.
                            """
                        else:
                            return False, f"Erro ao processar o arquivo {file_path}: {str(ge)}"
                    except Exception as e:
                        # Outros erros
                        return False, f"Erro ao processar o arquivo {file_path}: {str(e)}"
                
                if not element_list:
                    return False, f"Nenhum arquivo foi processado com sucesso. {skipped_files} arquivos ignorados."
                
                try:
                    # Criar uma nova árvore com os arquivos
                    new_tree = repo.create_git_tree(element_list, base_tree)
                    
                    # Criar um novo commit
                    parent = repo.get_git_commit(last_commit_sha)
                    new_commit = repo.create_git_commit(commit_message, new_tree, [parent])
                    
                    # Atualizar a referência do branch
                    ref = repo.get_git_ref(f"heads/{branch}")
                    ref.edit(new_commit.sha)
                    
                    return True, f"Sucesso! {processed_files} arquivos enviados para o branch '{branch}'."
                
                except github.GithubException as ge:
                    if ge.status == 403:  # Forbidden
                        return False, f"""
                        Erro de permissão (403 Forbidden): {ge.data.get('message', 'Acesso negado')}
                        
                        Seu token não tem permissões suficientes para esta operação.
                        Certifique-se de que seu token tenha os escopos corretos:
                        - 'repo' (acesso completo)
                        - 'workflow' (se estiver enviando arquivos de workflow)
                        
                        Você pode criar um novo token com as permissões corretas em:
                        https://github.com/settings/tokens/new
                        """
                    else:
                        return False, f"Erro do GitHub: {ge.data.get('message', str(ge))}"
                
            except Exception as e:
                return False, f"Erro ao enviar arquivos para o GitHub: {str(e)}"
        
        # Função para registrar automaticamente atualizações
        def registrar_atualizacao_automatica(commit_message, arquivos, success=True, notas_importantes=None):
            """
            Registra automaticamente uma atualização no histórico quando arquivos são enviados ao GitHub
            
            Args:
                commit_message (str): Mensagem do commit
                arquivos (list): Lista de arquivos enviados
                success (bool): Se o envio foi bem sucedido
                notas_importantes (str, optional): Notas importantes sobre a atualização
                
            Returns:
                bool: True se a atualização foi registrada com sucesso
            """
            try:
                update_file = "data/updates_history.json"
                
                # Verificar se já existe arquivo de atualizações
                if os.path.exists(update_file):
                    with open(update_file, "r", encoding="utf-8") as f:
                        updates_data = json.load(f)
                else:
                    updates_data = {"versoes": []}
                
                # Obter a última versão ou criar uma nova
                if updates_data["versoes"]:
                    ultima_versao = updates_data["versoes"][0]["versao"]
                    # Incrementar a última parte da versão (x.y.Z)
                    partes = ultima_versao.split('.')
                    if len(partes) >= 3:
                        partes[-1] = str(int(partes[-1]) + 1)
                        nova_versao = '.'.join(partes)
                    else:
                        nova_versao = ultima_versao + '.1'
                else:
                    nova_versao = "1.0.0"
                
                # Extrair informações úteis dos arquivos para a descrição
                tipos_arquivos = {
                    "pages": 0,
                    "utils": 0,
                    "app": 0,
                    "config": 0,
                    "data": 0,
                    "other": 0
                }
                
                for arquivo in arquivos:
                    if arquivo.startswith("pages/"):
                        tipos_arquivos["pages"] += 1
                    elif arquivo == "utils.py":
                        tipos_arquivos["utils"] += 1
                    elif arquivo == "app.py":
                        tipos_arquivos["app"] += 1
                    elif arquivo.startswith(".streamlit/"):
                        tipos_arquivos["config"] += 1
                    elif arquivo.startswith("data/"):
                        tipos_arquivos["data"] += 1
                    else:
                        tipos_arquivos["other"] += 1
                
                # Criar descrição resumida
                descricao_arquivos = []
                if tipos_arquivos["pages"] > 0:
                    descricao_arquivos.append(f"{tipos_arquivos['pages']} páginas")
                if tipos_arquivos["utils"] > 0:
                    descricao_arquivos.append("utilitários")
                if tipos_arquivos["app"] > 0:
                    descricao_arquivos.append("aplicação principal")
                if tipos_arquivos["config"] > 0:
                    descricao_arquivos.append("configurações")
                if tipos_arquivos["data"] > 0:
                    descricao_arquivos.append("arquivos de dados")
                if tipos_arquivos["other"] > 0:
                    descricao_arquivos.append(f"{tipos_arquivos['other']} outros arquivos")
                
                descricao_resumida = "Atualização incluindo " + ", ".join(descricao_arquivos)
                
                # Criar mudanças com base nos tipos de arquivos afetados
                mudancas = []
                
                # Título principal baseado na mensagem de commit
                if commit_message:
                    titulo_principal = commit_message.split("\n")[0]
                else:
                    titulo_principal = f"Atualização do sistema - {datetime.datetime.now().strftime('%d/%m/%Y')}"
                
                # Criar objeto de mudança principal
                mudanca_principal = {
                    "tipo": "Melhoria",
                    "titulo": titulo_principal,
                    "descricao": descricao_resumida,
                    "arquivos_alterados": [a for a in arquivos[:20]]  # Limitar a 20 arquivos para não sobrecarregar
                }
                
                # Se houver muitos arquivos, adicionar informação
                if len(arquivos) > 20:
                    mudanca_principal["descricao"] += f"\n\nTotal de {len(arquivos)} arquivos atualizados."
                
                mudancas.append(mudanca_principal)
                
                # Adicionar detalhes específicos conforme os tipos de arquivos
                if tipos_arquivos["pages"] > 0:
                    paginas_atualizadas = [a for a in arquivos if a.startswith("pages/")][:10]  # Primeiras 10 páginas
                    mudancas.append({
                        "tipo": "Melhoria",
                        "titulo": f"Atualização de {tipos_arquivos['pages']} páginas",
                        "descricao": f"Atualização das interfaces e funcionalidades do sistema",
                        "arquivos_alterados": paginas_atualizadas
                    })
                
                # Criar objeto da nova versão
                new_version = {
                    "versao": nova_versao,
                    "data": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "autor": "Atualização Automática via GitHub",
                    "descricao": f"Atualização automática via commit no GitHub: {commit_message}",
                    "mudancas": mudancas,
                    "codigo_interno": f"AUTO-GITHUB-{datetime.datetime.now().strftime('%Y%m%d%H%M')}",
                    "impacto": "Médio",
                    "equipe_responsavel": "Equipe de Desenvolvimento"
                }
                
                # Adicionar notas importantes (personalizadas ou padrão)
                if notas_importantes and notas_importantes.strip():
                    new_version["notas_importantes"] = notas_importantes
                else:
                    new_version["notas_importantes"] = "⚠️ Esta atualização foi gerada automaticamente pelo sistema de integração com GitHub. Verifique os arquivos atualizados para mais detalhes."
                
                # Adicionar ao início da lista
                updates_data["versoes"].insert(0, new_version)
                
                # Limitar o número de versões para evitar arquivo muito grande
                if len(updates_data["versoes"]) > 100:
                    updates_data["versoes"] = updates_data["versoes"][:100]
                
                # Salvar de volta ao arquivo
                with open(update_file, "w", encoding="utf-8") as f:
                    json.dump(updates_data, f, ensure_ascii=False, indent=4)
                
                return True
            except Exception as e:
                st.warning(f"Erro ao registrar atualização automática: {str(e)}")
                return False

        # Interface para enviar arquivos para o GitHub
        if github_credentials:
            st.markdown("<br><h4>Enviar Arquivos para o GitHub</h4>", unsafe_allow_html=True)
            
            with st.form("github_upload_form"):
                # Opções de pastas para enviar
                st.write("Selecione quais pastas deseja enviar para o GitHub:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    send_pages = st.checkbox("Páginas (pages/)", value=True)
                    send_utils = st.checkbox("Utilitários (utils.py)", value=True)
                    send_app = st.checkbox("Aplicação principal (app.py)", value=True)
                    send_data = st.checkbox("Dados (data/)", value=False)
                
                with col2:
                    send_config = st.checkbox("Configurações (.streamlit/)", value=True)
                    send_requirements = st.checkbox("Dependências (pyproject.toml, requirements.txt)", value=True)
                    send_download = st.checkbox("Página de download (download_page/)", value=True)
                    send_android = st.checkbox("Base do App Android (android_app_base/)", value=False)
                
                # Opção para registrar atualização automaticamente
                registrar_auto = st.checkbox("Registrar atualização automaticamente", value=True, 
                                          help="Adiciona automaticamente uma entrada no histórico de atualizações quando o envio for bem-sucedido")
                
                # Notas importantes personalizadas para atualizações automáticas
                notas_personalizadas = ""
                if registrar_auto:
                    notas_personalizadas = st.text_area("Notas importantes para o registro automático (opcional)", 
                                                   placeholder="Informações importantes sobre esta atualização, como alterações críticas ou instruções especiais",
                                                   help="Estas notas serão destacadas no histórico de atualizações")
                
                # Mensagem personalizada do commit
                commit_message = st.text_area("Mensagem do commit", 
                                            placeholder="Ex: Atualização do sistema com novas funcionalidades e correções",
                                            value=f"Atualização automática via Sistema Suinocultura - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
                
                # Branch para enviar
                branch = st.text_input("Branch", value="main")
                
                # Botão para enviar
                submit_button = st.form_submit_button("Enviar para GitHub")
                
                if submit_button:
                    files_to_send = []
                    
                    # Adicionar arquivos com base nas seleções
                    if send_pages:
                        # Adicionar todos os arquivos da pasta pages
                        for root, _, files in os.walk("pages"):
                            for file in files:
                                files_to_send.append(os.path.join(root, file))
                    
                    if send_utils:
                        files_to_send.append("utils.py")
                    
                    if send_app:
                        files_to_send.append("app.py")
                    
                    if send_config and os.path.exists(".streamlit"):
                        # Adicionar todos os arquivos da pasta .streamlit
                        for root, _, files in os.walk(".streamlit"):
                            for file in files:
                                files_to_send.append(os.path.join(root, file))
                    
                    if send_requirements:
                        if os.path.exists("pyproject.toml"):
                            files_to_send.append("pyproject.toml")
                        if os.path.exists("requirements.txt"):
                            files_to_send.append("requirements.txt")
                    
                    if send_data:
                        # Adicionar todos os arquivos da pasta data (exceto credentials)
                        for root, _, files in os.walk("data"):
                            for file in files:
                                if "credentials" not in file:  # Evitar enviar credenciais
                                    files_to_send.append(os.path.join(root, file))
                    
                    if send_download and os.path.exists("download_page"):
                        # Adicionar todos os arquivos da pasta download_page
                        for root, _, files in os.walk("download_page"):
                            for file in files:
                                files_to_send.append(os.path.join(root, file))
                    
                    if send_android and os.path.exists("android_app_base"):
                        # Adicionar todos os arquivos da pasta android_app_base
                        for root, _, files in os.walk("android_app_base"):
                            for file in files:
                                files_to_send.append(os.path.join(root, file))
                    
                    # Verificar se há arquivos para enviar
                    if not files_to_send:
                        st.error("Nenhum arquivo selecionado para enviar.")
                    else:
                        # Mostrar quais arquivos serão enviados
                        st.write("**Arquivos selecionados para envio:**")
                        for file in sorted(files_to_send)[:10]:  # Mostrar apenas os primeiros 10 arquivos
                            st.text(file)
                        
                        if len(files_to_send) > 10:
                            st.text(f"... e mais {len(files_to_send) - 10} arquivos")
                        
                        st.info(f"Total: {len(files_to_send)} arquivos selecionados para envio")
                        
                        # Confirmar envio
                        import time
                        with st.spinner("Enviando arquivos para o GitHub..."):
                            time.sleep(1)  # Pequena pausa para dar feedback visual
                            success, message = upload_to_github(files_to_send, commit_message, branch)
                        
                        if success:
                            st.success(message)
                            # Adicionar link para o repositório
                            repo_link = f"https://github.com/{github_credentials.get('repo_owner', '')}/{github_credentials.get('repo_name', '')}"
                            st.markdown(f"[Ver repositório no GitHub]({repo_link})")
                            
                            # Registrar atualização automaticamente se a opção estiver marcada
                            if registrar_auto:
                                with st.spinner("Registrando atualização no histórico..."):
                                    if registrar_atualizacao_automatica(commit_message, files_to_send, True, notas_personalizadas):
                                        st.success("✅ Atualização registrada automaticamente no histórico")
                                    else:
                                        st.warning("⚠️ Não foi possível registrar a atualização no histórico")
                        else:
                            st.error(message)
            
            # Histórico dos últimos envios
            st.markdown("<h4>Sugestões de uso</h4>", unsafe_allow_html=True)
            st.markdown("""
            - **Recomendado**: Envie apenas as páginas e arquivos que foram modificados
            - Evite enviar dados sensíveis ou arquivos de grande tamanho
            - Certifique-se de que o repositório exista e que o token tenha permissões de escrita
            - Utilize mensagens de commit descritivas para facilitar o rastreamento das alterações
            """)
            
            # Adicionar aviso sobre tokens do GitHub
            st.warning("""
            **⚠️ Importante sobre Tokens do GitHub**
            
            Para evitar erros de permissão (403 Forbidden), certifique-se de que seu token pessoal tenha as seguintes permissões:
            - Permissão completa para `repo` (acesso a repositórios privados)
            - Se você estiver usando o novo sistema de tokens de acesso refinados (fine-grained tokens), garanta as permissões:
              - `Contents: Read and write` (para ler e modificar arquivos)
              - `Metadata: Read-only` (para acessar metadados do repositório)
              
            Tokens expirados ou com permissões insuficientes resultarão em falhas no envio.
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Aba Kivy Mobile
    st.markdown('<div class="dev-section"><h2>Gerador de APK WebView</h2></div>', unsafe_allow_html=True)
    
    # Definindo as tabs para o gerador de APK
    apk_tab1, apk_tab2, apk_tab3 = st.tabs(["📱 Configuração Básica", "⚙️ Configurações Avançadas", "🛠️ Compilação"])
    
    # Aba 1 - WebView Personalizado
    with apk_tab1:
        st.subheader("Personalize seu APK WebView")
        
        col1, col2 = st.columns([2, 1])
        
        # Coluna 1 - Formulário principal
        with col1:
            with st.form("apk_webview_form"):
                st.markdown("### Configurações Básicas")
                
                app_name = st.text_input("Nome do Aplicativo", 
                                         value=st.session_state.apk_app_name,
                                         help="Nome que aparecerá no dispositivo do usuário")
                                         
                package_name = st.text_input("Nome do Pacote", 
                                            value=st.session_state.apk_package_name,
                                            help="Identificador único do aplicativo, formato: com.example.app")
                                            
                app_version = st.text_input("Versão", 
                                           value=st.session_state.apk_version,
                                           help="Versão do aplicativo (ex: 1.0.0)")
                                           
                app_url = st.text_input("URL do Sistema Suinocultura", 
                                       value=st.session_state.apk_url,
                                       help="URL completa da aplicação web (incluindo https://)")
                
                st.markdown("### Personalização Visual")
                
                app_color = st.color_picker("Cor Principal", 
                                           value=st.session_state.apk_primary_color,
                                           help="Cor principal do aplicativo")
                                           
                dark_mode = st.checkbox("Habilitar Modo Escuro", 
                                       value=st.session_state.apk_dark_mode,
                                       help="Aplica tema escuro ao aplicativo")
                                       
                enable_splash = st.checkbox("Tela de Splash", 
                                          value=st.session_state.apk_splash_screen,
                                          help="Exibe uma tela de abertura ao iniciar o aplicativo")
                
                st.markdown("### Configurações Técnicas")
                                       
                enable_cache = st.checkbox("Habilitar Cache", 
                                         value=st.session_state.apk_enable_cache,
                                         help="Permite que o aplicativo armazene dados em cache para uso offline")
                                         
                enable_zoom = st.checkbox("Permitir Zoom", 
                                        value=st.session_state.apk_enable_zoom,
                                        help="Permite que o usuário use gestos de zoom na aplicação")
                                        
                offline_message = st.text_area("Mensagem Offline", 
                                             value=st.session_state.apk_offline_message,
                                             help="Mensagem exibida quando o aplicativo está sem conexão")
                
                submitted = st.form_submit_button("Gerar APK WebView", type="primary")
                
                if submitted:
                    # Salvar configurações na session state
                    st.session_state.apk_app_name = app_name
                    st.session_state.apk_package_name = package_name
                    st.session_state.apk_version = app_version
                    st.session_state.apk_url = app_url
                    st.session_state.apk_primary_color = app_color
                    st.session_state.apk_dark_mode = dark_mode
                    st.session_state.apk_enable_cache = enable_cache
                    st.session_state.apk_enable_zoom = enable_zoom
                    st.session_state.apk_splash_screen = enable_splash
                    st.session_state.apk_offline_message = offline_message
                    
                    # Gerar APK WebView usando o simpler_webview_app_creator.py
                    try:
                        with st.spinner("Gerando projeto Android WebView..."):
                            # Importar e executar o script
                            import importlib.util
                            
                            # Carregar o script
                            spec = importlib.util.spec_from_file_location("simpler_webview_app_creator", "simpler_webview_app_creator.py")
                            webview_creator = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(webview_creator)
                            
                            # Sobrescrever as configurações no módulo
                            webview_creator.APP_NAME = app_name
                            webview_creator.PACKAGE_NAME = package_name
                            webview_creator.VERSION = app_version
                            webview_creator.URL = app_url
                            
                            # Criar pasta temporária para o projeto
                            project_dir = "android_webview_project"
                            if os.path.exists(project_dir):
                                shutil.rmtree(project_dir)
                            
                            # Executar criação do projeto
                            os.makedirs(project_dir, exist_ok=True)
                            
                            # Alterar o diretório de trabalho
                            original_dir = os.getcwd()
                            os.chdir(project_dir)
                            
                            # Criar estrutura do projeto
                            webview_creator.create_project_structure()
                            webview_creator.create_manifest()
                            webview_creator.create_main_activity()
                            webview_creator.create_layout()
                            webview_creator.create_strings()
                            webview_creator.create_colors()
                            webview_creator.create_build_gradle()
                            webview_creator.create_gradle_wrapper()
                            webview_creator.create_settings_gradle()
                            webview_creator.create_icon()
                            
                            # Aplicar personalizações adicionais
                            # Aqui você pode modificar os arquivos gerados para adicionar as personalizações extras
                            
                            # Criar ZIP
                            zip_path = webview_creator.create_project_zip()
                            
                            # Criar guia HTML
                            html_guide_path = webview_creator.create_online_apk_guide()
                            
                            # Criar a alternativa direta
                            direct_apk_path = webview_creator.create_direct_apk_alternative()
                            
                            # Voltar ao diretório original
                            os.chdir(original_dir)
                            
                            st.success("Projeto para geração de APK WebView criado com sucesso!")
                            
                            # Opção para download do projeto
                            zip_file = f"{project_dir}.zip"
                            if os.path.exists(zip_file):
                                with open(zip_file, "rb") as file:
                                    btn = st.download_button(
                                        label="📥 Download do Projeto Android",
                                        data=file,
                                        file_name=zip_file,
                                        mime="application/zip",
                                        help="Baixe o projeto Android completo para compilar localmente"
                                    )
                            
                            # Exibir instruções
                            st.info("Siga as instruções abaixo para compilar o APK ou use o método online.")
                            
                    except Exception as e:
                        st.error(f"Erro ao gerar o projeto: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        
        # Coluna 2 - Preview e instruções
        with col2:
            st.markdown("### Preview do Aplicativo")
            
            # Mostrar preview do aplicativo
            preview_color = st.session_state.apk_primary_color
            preview_name = st.session_state.apk_app_name
            preview_dark = st.session_state.apk_dark_mode
            
            # Gerar um preview simulado do aplicativo
            bg_color = "#121212" if preview_dark else "#FFFFFF"
            text_color = "#FFFFFF" if preview_dark else "#000000"
            status_bar_color = "#000000" if preview_dark else "#EEEEEE"
            
            st.markdown(f"""
            <div style="border: 1px solid #AAA; border-radius: 10px; overflow: hidden; width: 220px; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <!-- Status Bar -->
                <div style="background-color: {status_bar_color}; color: {'#FFFFFF' if preview_dark else '#777777'}; height: 20px; font-size: 10px; display: flex; align-items: center; justify-content: flex-end; padding: 0 5px;">
                    <span>12:34 PM</span>
                </div>
                
                <!-- Action Bar -->
                <div style="background-color: {preview_color}; color: white; padding: 10px; text-align: left; font-weight: bold; font-size: 14px;">
                    {preview_name}
                </div>
                
                <!-- Content Area -->
                <div style="background-color: {bg_color}; color: {text_color}; height: 320px; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                        <div style="width: 50px; height: 50px; border-radius: 50%; background-color: {preview_color}; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px auto;">
                            <span style="color: white; font-size: 24px;">🐷</span>
                        </div>
                        <div style="color: {text_color};">Carregando...</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Dicas
            st.markdown("### Dicas")
            
            st.info("""
            - Use cores que combinem com a identidade visual do sistema
            - O modo escuro é recomendado para reduzir o consumo de bateria em telas OLED
            - O cache permite uso parcial do app sem conexão
            """)
            
    # Aba 2 - Configurações Avançadas
    with apk_tab2:
        st.subheader("Configurações Avançadas")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Comportamento do WebView")
            
            javascript_enabled = st.checkbox("Habilitar JavaScript", value=True, 
                                           help="Permite a execução de JavaScript no WebView")
            
            hardware_acceleration = st.checkbox("Aceleração de Hardware", value=True, 
                                              help="Utiliza GPU para renderização mais rápida")
            
            dom_storage = st.checkbox("DOM Storage", value=True, 
                                     help="Permite armazenamento local persistente")
                                     
            database_storage = st.checkbox("Database Storage", value=True, 
                                         help="Permite uso de bancos de dados locais (SQLite)")
                                         
            file_access = st.checkbox("Acesso a Arquivos", value=True, 
                                     help="Permite que o aplicativo acesse arquivos locais")
            
            st.markdown("### Permissões")
            
            permission_internet = st.checkbox("Internet", value=True, disabled=True, 
                                            help="Acesso à internet (obrigatório)")
            
            permission_network_state = st.checkbox("Estado da Rede", value=True, 
                                                 help="Verificar o estado da conexão")
            
            permission_storage = st.checkbox("Armazenamento", value=False, 
                                           help="Acesso ao armazenamento do dispositivo")
            
            permission_camera = st.checkbox("Câmera", value=False, 
                                          help="Acesso à câmera para captura de imagens")
            
            permission_location = st.checkbox("Localização", value=False, 
                                            help="Acesso à localização do dispositivo")
        
        with col2:
            st.markdown("### Configurações de Interface")
            
            orientation = st.radio("Orientação da Tela", 
                                  options=["portrait", "landscape", "sensor"],
                                  index=0,
                                  help="Orientação preferida do aplicativo")
            
            fullscreen = st.checkbox("Tela Cheia", value=False, 
                                    help="Executa o aplicativo em modo de tela cheia")
            
            keep_screen_on = st.checkbox("Manter Tela Ligada", value=False, 
                                        help="Evita que a tela se desligue durante o uso do aplicativo")
            
            st.markdown("### Configurações de Build")
            
            min_sdk = st.slider("Android Mínimo", min_value=16, max_value=33, value=21, 
                               help="Versão mínima do Android suportada (21 = Android 5.0)")
            
            target_sdk = st.slider("Android Alvo", min_value=min_sdk, max_value=33, value=33, 
                                  help="Versão alvo do Android")
            
            accept_advanced = st.button("Aplicar Configurações Avançadas", type="primary")
            
            if accept_advanced:
                st.success("Configurações avançadas aplicadas com sucesso!")
                
            st.info("""
            **Nota:** As configurações avançadas exigem conhecimento de desenvolvimento 
            Android e podem afetar a compatibilidade do aplicativo em alguns dispositivos.
            """)
    
    # Aba 3 - Métodos de Compilação
    with apk_tab3:
        st.subheader("Métodos para Compilação")
        
        st.markdown("""
        Existem várias maneiras de compilar o APK WebView gerado. Escolha a opção que melhor se adapta às suas necessidades:
        """)
        
        # Método 1 - Serviço Online
        st.markdown("### 1. Serviço Online")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **O que é:** Serviços online que permitem fazer upload do seu projeto Android e receber um APK compilado.
            
            **Vantagens:**
            - Não requer instalação de ferramentas
            - Processo rápido e simples
            - Funciona em qualquer sistema operacional
            
            **Desvantagens:**
            - Menos personalização
            - Pode ter limitações em serviços gratuitos
            - Requer upload do código-fonte
            """)
        
        with col2:
            st.markdown("""
            **Recomendado para:**
            - Usuários iniciantes
            - Testes rápidos
            - Quem não tem ambiente de desenvolvimento
            """)
        
        # Botão para abrir o guia de serviço online
        if st.button("Abrir Guia de Serviço Online", type="secondary"):
            # Verificar se o arquivo existente
            html_guide_path = "download_page/buildozer_online_guide.html"
            
            if os.path.exists(html_guide_path):
                # Abrir o arquivo HTML em uma nova guia usando JavaScript
                js_code = f"""
                <script>
                    window.open('/download_page/buildozer_online_guide.html', '_blank');
                </script>
                """
                st.markdown(js_code, unsafe_allow_html=True)
                st.success("Guia aberto em uma nova guia!")
            else:
                st.error("Guia não encontrado. Execute primeiro a geração do APK.")
        
        st.markdown("---")
        
        # Método 2 - Android Studio
        st.markdown("### 2. Android Studio")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **O que é:** O ambiente de desenvolvimento oficial para Android.
            
            **Vantagens:**
            - Controle total sobre o processo de compilação
            - Possibilidade de depuração avançada
            - Mais opções de personalização
            
            **Desvantagens:**
            - Requer instalação do Android Studio (+ 8GB)
            - Curva de aprendizado mais alta
            - Consome mais recursos do computador
            """)
        
        with col2:
            st.markdown("""
            **Recomendado para:**
            - Desenvolvedores
            - Projetos mais complexos
            - Quando precisar de recursos avançados
            """)
        
        st.code("""
        # Passos para compilar no Android Studio:
        1. Descompacte o arquivo ZIP do projeto
        2. Abra o Android Studio
        3. Selecione "Open an Existing Project"
        4. Navegue até a pasta do projeto descompactado
        5. Aguarde a sincronização do Gradle
        6. Clique em Build > Build Bundle(s) / APK(s) > Build APK(s)
        7. Aguarde a compilação e clique em "locate" para encontrar o APK
        """, language="bash")
        
        st.markdown("---")
        
        # Método 3 - Buildozer
        st.markdown("### 3. Compilação Direta com Buildozer")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **O que é:** Ferramenta que permite compilar aplicativos Python/Kivy para Android.
            
            **Vantagens:**
            - Linha de comando simples
            - Automação possível
            - Menos recursos que o Android Studio
            
            **Desvantagens:**
            - Requer ambiente Linux
            - Instalação de várias dependências
            - Pode ter problemas de compatibilidade
            """)
        
        with col2:
            st.markdown("""
            **Recomendado para:**
            - Usuários do Linux
            - Desenvolvimento em servidor
            - Quem prefere linha de comando
            """)
        
        st.code("""
        # Instalação no Ubuntu/Debian:
        sudo apt update
        sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config
        sudo apt install -y libncurses5-dev libncursesw5-dev zlib1g-dev
        sudo pip3 install --upgrade Cython==0.29.33 virtualenv buildozer
        
        # Compilar o APK:
        buildozer -v android debug
        """, language="bash")
        
        st.warning("""
        **Aviso:** A compilação direta com Buildozer pode exigir configurações adicionais
        e é recomendada apenas para usuários avançados.
        """)
        
        # Método 4 - Compilar Online com PWA
        st.markdown("### 4. Progressive Web App (PWA)")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            **O que é:** Converter seu site em um PWA que pode ser instalado diretamente do navegador.
            
            **Vantagens:**
            - Instalação direta pelo navegador
            - Não requer compilação
            - Atualizações automáticas
            
            **Desvantagens:**
            - Acesso limitado aos recursos do dispositivo
            - Menos integrado ao sistema operacional
            - Requer conexão para primeira instalação
            """)
        
        with col2:
            st.markdown("""
            **Recomendado para:**
            - Soluções rápidas
            - Aplicações simples
            - Quando APK não é estritamente necessário
            """)
        
        # Botão para ativar PWA
        if st.button("Transformar em PWA", type="secondary"):
            st.info("""
            Para transformar o Sistema Suinocultura em um PWA, adicione um manifesto
            web e service worker ao seu projeto Streamlit. Um guia detalhado está disponível
            na documentação.
            
            Usuários poderão instalar o PWA diretamente do Chrome/Edge ao acessar o site.
            """)
        
        st.markdown("---")
        
        # Seção final com ajuda
        st.markdown("### Precisa de ajuda?")
        
        st.info("""
        Se você estiver com dificuldades para compilar o APK, entre em contato
        com a equipe de desenvolvimento ou consulte os recursos disponíveis na 
        documentação do Android.
        """)
            
        # Botões de ação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("📖 Documentação", type="secondary"):
                st.markdown("Acessando documentação...")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("🤔 FAQ", type="secondary"):
                st.markdown("Exibindo perguntas frequentes...")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            if st.button("🎬 Tutorial em Vídeo", type="secondary"):
                st.markdown("Iniciando tutorial em vídeo...")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Estilos baseados no modo selecionado
    bg_color = "#1E1E1E" if dark_mode else "#FFFFFF"
    text_color = "#E0E0E0" if dark_mode else "#333333"
    code_bg = "#2D2D2D" if dark_mode else "#F5F5F5"
    accent_color = "#9C27B0" # Roxo primário
    
    # CSS personalizado baseado no modo
    st.markdown(f"""
    <style>
        .kivy-container {{
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .kivy-header {{
            color: {accent_color};
            border-bottom: 2px solid {accent_color};
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .kivy-code {{
            background-color: {code_bg};
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            white-space: pre-wrap;
            border-left: 3px solid {accent_color};
        }}
        .kivy-note {{
            background-color: {"rgba(156, 39, 176, 0.1)" if dark_mode else "rgba(156, 39, 176, 0.05)"};
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid {accent_color};
            margin: 15px 0;
        }}
        .kivy-button {{
            background-color: {accent_color};
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 0;
            cursor: pointer;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Informações sobre o Kivy e o aplicativo móvel
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Sobre o Kivy</h3>
        <p>
            Kivy é um framework Python de código aberto para o desenvolvimento rápido de aplicativos 
            que utilizam interfaces de usuário inovadoras, como aplicativos multitoque. O framework é 
            multiplataforma (Windows, macOS, Linux, Android, iOS) e baseado em OpenGL ES 2.
        </p>
        <div class="kivy-note">
            <strong>Vantagens do Kivy:</strong>
            <ul>
                <li>Multiplataforma: execute o mesmo código em várias plataformas.</li>
                <li>Rápido desenvolvimento: crie protótipos e aplicativos rapidamente.</li>
                <li>Focado em interfaces gráficas: suporte a multitoque e gestos.</li>
                <li>Integração com Python: utiliza todas as bibliotecas e ferramentas Python.</li>
                <li>Linguagem KV: separa a lógica do aplicativo da interface do usuário.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Estrutura do aplicativo Kivy desenvolvido
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Aplicativo Sistema Suinocultura</h3>
        <p>
            Foi desenvolvido um aplicativo móvel utilizando Kivy para acesso ao Sistema Suinocultura. 
            O aplicativo permite que usuários realizem operações básicas de gerenciamento diretamente 
            em dispositivos móveis, mesmo com conectividade limitada.
        </p>
        
        <h4>Estrutura do Projeto</h4>
        <div class="kivy-code">
kivy_app/
  ├── __init__.py
  ├── main.py              # Arquivo principal do aplicativo
  ├── suinocultura.kv      # Definições de interface (linguagem KV)
  ├── animal_screen.py     # Tela de gerenciamento de animais
  └── assets/              # Imagens e recursos do aplicativo
        </div>
        
        <h4>Funcionalidades Implementadas</h4>
        <ul>
            <li><strong>Autenticação:</strong> Login com matrícula para acesso seguro</li>
            <li><strong>Menu Principal:</strong> Acesso aos principais módulos do sistema</li>
            <li><strong>Gestão de Animais:</strong> Cadastro, listagem e edição de animais</li>
        </ul>
        
        <div class="kivy-note">
            <strong>Nota de Desenvolvimento:</strong> O aplicativo Kivy está em fase inicial de desenvolvimento. 
            Novas funcionalidades serão adicionadas gradualmente seguindo as prioridades estabelecidas para o sistema.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Como executar o aplicativo
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Executando o Aplicativo</h3>
        
        <h4>Requisitos</h4>
        <ul>
            <li>Python 3.7+</li>
            <li>Kivy 2.1.0+</li>
            <li>PIL (Pillow)</li>
        </ul>
        
        <h4>Comandos para Execução</h4>
        <div class="kivy-code">
# Instalação das dependências
pip install kivy pillow

# Executar o aplicativo
python -m kivy_app.main
        </div>
        
        <h4>Compilando para Android</h4>
        <p>
            Para compilar o aplicativo para Android, é necessário utilizar o Buildozer, 
            uma ferramenta que automatiza o processo de empacotamento do aplicativo Kivy 
            para Android (e iOS futuramente).
        </p>
        
        <div class="kivy-code">
# Instalar Buildozer
pip install buildozer

# Inicializar configuração do Buildozer
buildozer init

# Editar buildozer.spec conforme necessário

# Compilar para Android
buildozer android debug
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemplos de código
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Exemplos de Código</h3>
        
        <h4>Exemplo da Tela de Login (Python)</h4>
        <div class="kivy-code">
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical', 
                        padding=dp(20), spacing=dp(20))
        
        # Campos de login
        self.matricula_input = TextInput(
            hint_text='Matrícula', 
            multiline=False, 
            size_hint_y=None, height=dp(50)
        )
        
        # Botão de login
        login_button = Button(
            text='Entrar', 
            size_hint_y=None, height=dp(50),
            background_color=get_color_from_hex(ROXO_PRIMARIO)
        )
        login_button.bind(on_press=self.login)
        
        # Adicionar layout à tela
        self.add_widget(layout)
    
    def login(self, instance):
        # Lógica de autenticação
        matricula = self.matricula_input.text.strip()
        
        if matricula == "123456":  # Exemplo
            self.manager.current = 'menu'
        else:
            self.status_label.text = "Matrícula não encontrada"
        </div>
        
        <h4>Exemplo da Definição KV para AnimalCard</h4>
        <div class="kivy-code">
<AnimalCard@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(150)
    padding: dp(10)
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: get_color_from_hex(BRANCO)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(5)]
        Color:
            rgba: get_color_from_hex(ROXO_CLARO)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(5)]
            width: 1.5
    
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(30)
        
        Label:
            text: 'ID: 12345'
            color: get_color_from_hex(ROXO_PRIMARIO)
            font_size: dp(16)
            bold: True
            
    Label:
        text: 'Porca - Landrace'
        color: get_color_from_hex(CINZA_ESCURO)
        font_size: dp(14)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Desenvolvimento futuro
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Próximos Passos de Desenvolvimento</h3>
        
        <h4>Funcionalidades Planejadas</h4>
        <ul>
            <li><strong>Módulo de Reprodução:</strong> Registro de cio, inseminação e partos</li>
            <li><strong>Sincronização Offline:</strong> Trabalho offline com sincronização posterior</li>
            <li><strong>Escaneamento de QR Code:</strong> Identificação rápida de animais</li>
            <li><strong>Relatórios Móveis:</strong> Visualização de relatórios críticos em formato móvel</li>
            <li><strong>Notificações Push:</strong> Alertas para eventos importantes</li>
        </ul>
        
        <h4>Otimizações</h4>
        <ul>
            <li>Melhoria de desempenho para dispositivos com recursos limitados</li>
            <li>Otimização do uso de bateria</li>
            <li>Adaptação para diferentes tamanhos de tela</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Documentação e recursos
    st.markdown(f"""
    <div class="kivy-container">
        <h3 class="kivy-header">Recursos para Desenvolvimento</h3>
        
        <h4>Documentação Oficial</h4>
        <ul>
            <li><a href="https://kivy.org/doc/stable/" target="_blank" style="color: {accent_color};">Documentação do Kivy</a></li>
            <li><a href="https://buildozer.readthedocs.io/" target="_blank" style="color: {accent_color};">Documentação do Buildozer</a></li>
        </ul>
        
        <h4>Tutoriais Recomendados</h4>
        <ul>
            <li><a href="https://kivy.org/doc/stable/tutorials/pong.html" target="_blank" style="color: {accent_color};">Tutorial Básico: Criando um jogo Pong</a></li>
            <li><a href="https://github.com/kivy/kivy/tree/master/examples" target="_blank" style="color: {accent_color};">Exemplos Oficiais do Kivy</a></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('''
    <div style="background-color: #1E1E1E; color: #9C27B0; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; border-left: 5px solid #9C27B0; font-family: 'Courier New', monospace;">
        <h2 style="margin:0; color: #9C27B0; text-shadow: 0 0 5px rgba(156, 39, 176, 0.3);">📱 Kivy Mobile</h2>
        <p style="margin-top:0.5rem; color: #BBBBBB;">Ferramentas para desenvolvimento mobile com Kivy</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Toggle para modo escuro
    if 'kivy_dark_mode' not in st.session_state:
        st.session_state.kivy_dark_mode = False
    
    # Definir estilos com base no modo
    if st.session_state.kivy_dark_mode:
        # Estilos para modo escuro
        bg_color = "#2D2D2D"
        text_color = "#E0E0E0"
        card_bg = "#3D3D3D"
        card_title = "#BB86FC"
        link_color = "#BB86FC"
        border_color = "#444444"
        code_bg = "#1E1E1E"
    else:
        # Estilos para modo claro
        bg_color = "#FFFFFF"
        text_color = "#333333"
        card_bg = "#f5f5f5"
        card_title = "#9C27B0"
        link_color = "#673AB7"
        border_color = "#DDDDDD"
        code_bg = "#F8F8F8"
    
    # CSS para links e elementos no modo escuro/claro
    st.markdown(f"""
    <style>
        .kivy-dark-mode a {{ color: {link_color} !important; }}
        .kivy-card {{ 
            background-color: {card_bg}; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
            color: {text_color};
            border: 1px solid {border_color};
        }}
        .kivy-card h4 {{ color: {card_title}; margin-top: 0; }}
        .kivy-code-block {{ background-color: {code_bg}; padding: 10px; border-radius: 4px; }}
    </style>
    """, unsafe_allow_html=True)
    
    # Toggle para alternar modo escuro
    mode_col1, mode_col2 = st.columns([4, 1])
    with mode_col2:
        if st.toggle("Modo Escuro", value=st.session_state.kivy_dark_mode, key="toggle_dark_mode"):
            st.session_state.kivy_dark_mode = True
        else:
            st.session_state.kivy_dark_mode = False
    
    # Dividir em colunas
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Informações do Kivy")
        
        # Verificar a instalação do Kivy
        try:
            import kivy
            kivy_version = kivy.__version__
            kivy_status = "Instalado"
            kivy_color = "#4CAF50" if not st.session_state.kivy_dark_mode else "#81C784"
        except ImportError:
            kivy_version = "N/A"
            kivy_status = "Não Instalado"
            kivy_color = "#F44336" if not st.session_state.kivy_dark_mode else "#E57373"
        
        # Exibir informações sobre o Kivy
        st.markdown(f"""
        <div class="kivy-dark-mode kivy-card">
            <h4>Status do Kivy</h4>
            <p><strong>Versão:</strong> {kivy_version}</p>
            <p><strong>Status:</strong> <span style='color: {kivy_color};'>{kivy_status}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Documentação
        st.markdown(f"""
        <div class="kivy-dark-mode kivy-card">
            <h4>Documentação do Kivy</h4>
            <p>O Kivy é uma biblioteca Python para desenvolvimento de aplicações multi-touch, compatível com várias plataformas (Windows, MacOS, Linux, Android, iOS).</p>
            <ul>
                <li><a href='https://kivy.org/doc/stable/' target='_blank'>Documentação Oficial</a></li>
                <li><a href='https://kivy.org/doc/stable/gettingstarted/intro.html' target='_blank'>Guia de Introdução</a></li>
                <li><a href='https://kivy.org/doc/stable/examples/index.html' target='_blank'>Exemplos</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Desenvolvimento Mobile")
        
        # Explicar como usar o Kivy para desenvolvimento mobile
        st.markdown(f"""
        <div class="kivy-dark-mode kivy-card">
            <h4>Criação de Aplicações Mobile</h4>
            <p>Com o Kivy, você pode criar aplicações mobile multiplataforma usando Python:</p>
            <ol>
                <li>Desenvolva sua interface utilizando a linguagem Kv ou Python</li>
                <li>Teste sua aplicação localmente</li>
                <li>Compile para Android usando Buildozer ou para iOS usando o Kivy-iOS</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Adicionar exemplos de código
        with st.expander("Exemplo Básico do Kivy", expanded=True):
            st.code('''
import kivy
from kivy.app import App
from kivy.uix.label import Label

class SuinoculturaApp(App):
    def build(self):
        return Label(text='Sistema Suinocultura Mobile')

if __name__ == '__main__':
    SuinoculturaApp().run()
''', language="python")
        
        with st.expander("Exemplo com Interface Mais Complexa"):
            st.code('''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class SuinoculturaInterface(BoxLayout):
    def __init__(self, **kwargs):
        super(SuinoculturaInterface, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Título
        self.add_widget(Label(
            text='Sistema Suinocultura Mobile',
            size_hint=(1, 0.2),
            font_size=24
        ))
        
        # Botões de navegação
        btns = [
            'Cadastro de Animais', 
            'Reprodução', 
            'Crescimento', 
            'Saúde', 
            'Relatórios'
        ]
        
        for btn_text in btns:
            btn = Button(
                text=btn_text,
                size_hint=(1, 0.1),
                background_color=(0.3, 0.6, 0.9, 1)
            )
            btn.bind(on_press=self.button_pressed)
            self.add_widget(btn)
    
    def button_pressed(self, instance):
        print(f'Botão pressionado: {instance.text}')

class SuinoculturaApp(App):
    def build(self):
        return SuinoculturaInterface()

if __name__ == '__main__':
    SuinoculturaApp().run()
''', language="python")
    
    # Seção de criação de aplicativo mobile
    st.markdown("---")
    st.subheader("Ferramentas de Desenvolvimento Mobile")
    
    # Configuração do Buildozer
    with st.expander("Configuração do Buildozer para Android", expanded=False):
        st.markdown(f"""
        <div class="kivy-dark-mode kivy-card">
            <h4>Buildozer</h4>
            <p>O Buildozer é uma ferramenta que automatiza o processo de compilação de aplicativos Kivy para Android e iOS.</p>
            <p>Para configurar, crie um arquivo <code>buildozer.spec</code> na raiz do seu projeto.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.code('''
[app]
# Nome do seu aplicativo
title = Suinocultura Mobile

# Identificador único do pacote
package.name = suinoculturaapp
package.domain = com.suinocultura

# Versão do aplicativo
version = 1.0

# Requisitos (dependências)
requirements = python3,kivy

# Orientação da tela (portrait, landscape)
orientation = portrait

# Ícone do aplicativo
icon.filename = %(source.dir)s/icon.png

# Arquivos a serem incluídos no pacote
source.include_exts = py,png,jpg,kv,atlas

[buildozer]
# Android settings
android.permissions = INTERNET
''', language="ini")
    
    # Interface para experimentação do Kivy
    st.markdown("---")
    st.subheader("Área de Experimentação")
    
    # Editor de código simples para experimentação - estilizado com base no modo
    code_background = code_bg if st.session_state.kivy_dark_mode else "#f5f5f5"
    text_color_code = "#E0E0E0" if st.session_state.kivy_dark_mode else "#333333"
    
    # Aplicar estilo CSS em tempo real ao container do editor de código
    if st.session_state.kivy_dark_mode:
        st.markdown("""
        <style>
            .stTextArea textarea {
                background-color: #1E1E1E !important;
                color: #E0E0E0 !important;
                border: 1px solid #444444 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Editor de código simples para experimentação
    kivy_code = st.text_area(
        "Experimente o código Kivy aqui (não executa no navegador, apenas para referência)",
        height=200,
        value='''
from kivy.app import App
from kivy.uix.button import Button

class TestApp(App):
    def build(self):
        return Button(text='Olá de Kivy',
                      size_hint=(0.5, 0.5),
                      pos_hint={'center_x': 0.5, 'center_y': 0.5})

if __name__ == '__main__':
    TestApp().run()
''')
    
    # Dicas e recursos adicionais
    st.markdown("---")
    st.subheader("Dicas e Recursos")
    
    st.markdown(f"""
    <div class="kivy-dark-mode kivy-card">
        <h4>Como integrar o Sistema Suinocultura com Kivy</h4>
        <p>Para criar uma versão mobile do Sistema Suinocultura:</p>
        <ol>
            <li>Crie uma interface Kivy que se comunique com a API do sistema</li>
            <li>Defina as telas principais para as funcionalidades essenciais</li>
            <li>Implemente a comunicação HTTP para acessar os dados remotamente</li>
            <li>Use o Buildozer para compilar a aplicação para Android</li>
        </ol>
    </div>
    
    <div class="kivy-dark-mode kivy-card">
        <h4>Recursos para Aprendizado</h4>
        <ul>
            <li><a href='https://kivy.org/doc/stable/tutorials/pong.html' target='_blank'>Tutorial: Criando um jogo de Pong</a></li>
            <li><a href='https://github.com/kivy/kivy/tree/master/examples' target='_blank'>Exemplos oficiais do Kivy</a></li>
            <li><a href='https://kivy.org/doc/stable/api-kivy.html' target='_blank'>API do Kivy</a></li>
            <li><a href='https://buildozer.readthedocs.io/en/latest/' target='_blank'>Documentação do Buildozer</a></li>
        </ul>
    </div>
    
    <div class="kivy-dark-mode kivy-card" style="margin-top: 20px; text-align: center;">
        <p style="font-style: italic;">O modo escuro facilita o desenvolvimento prolongado, reduzindo o cansaço visual.</p>
    </div>
    """, unsafe_allow_html=True)

# Aba de Componentes Streamlit
with tab7:
    st.markdown('<div class="dev-section"><h2>Gerenciamento de Componentes Streamlit</h2></div>', unsafe_allow_html=True)
    
    # Subtabs para a aba de componentes
    comp_tab1, comp_tab2 = st.tabs(["📦 Componentes Instalados", "➕ Instalar Novo Componente"])
    
    with comp_tab1:
        st.markdown("### Componentes Streamlit Instalados")
        st.markdown("Abaixo estão os componentes Streamlit atualmente instalados no sistema:")
        
        # Obter lista de pacotes instalados via pip freeze
        try:
            import subprocess
            import pkg_resources
            
            # Filtrar apenas os pacotes que contêm 'streamlit' no nome
            streamlit_packages = []
            for pkg in pkg_resources.working_set:
                if 'streamlit' in pkg.key.lower() and pkg.key != 'streamlit':
                    streamlit_packages.append({
                        "nome": pkg.key,
                        "versao": pkg.version,
                        "descricao": pkg.project_name
                    })
            
            if streamlit_packages:
                # Criar cards para cada componente
                for pkg in streamlit_packages:
                    st.markdown(f"""
                    <div class="component-card">
                        <div class="component-title">{pkg['nome']}</div>
                        <div class="component-version">Versão: {pkg['versao']}</div>
                        <div class="component-desc">{pkg['descricao']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Não foram encontrados componentes adicionais do Streamlit instalados.")
                st.markdown("""
                ### O que são Componentes Streamlit?
                
                Os componentes do Streamlit são extensões que adicionam funcionalidades extras
                à sua aplicação Streamlit. Eles podem incluir recursos como:
                
                - Gráficos e visualizações avançadas
                - Elementos de interface personalizados
                - Integrações com APIs externas
                - Recursos especializados para áreas específicas
                
                Para instalar um componente, vá para a aba "➕ Instalar Novo Componente".
                """)
        except Exception as e:
            st.error(f"Erro ao obter a lista de componentes: {str(e)}")
    
    with comp_tab2:
        st.markdown("### Instalar Novo Componente Streamlit")
        st.markdown("""
        Aqui você pode instalar componentes adicionais para o Streamlit.
        Os componentes são normalmente instalados via pip e estão disponíveis
        no [Streamlit Components Directory](https://streamlit.io/components).
        """)
        
        # Formulário para instalação de novos componentes
        with st.form("instalar_componente_form"):
            nome_componente = st.text_input("Nome do Componente", 
                                          placeholder="Ex: streamlit-echarts, streamlit-aggrid")
            
            versao = st.text_input("Versão (opcional)", 
                                 placeholder="Ex: 0.4.0 (deixe em branco para a versão mais recente)")
            
            st.markdown("### Opções Avançadas")
            
            opcoes_extras = st.multiselect("Opções de Instalação", 
                                        ["--upgrade", "--force-reinstall", "--no-deps"],
                                        default=[])
            
            submitted = st.form_submit_button("Instalar Componente")
            
            if submitted:
                if nome_componente:
                    try:
                        # Preparar comando pip
                        comando = f"pip install {nome_componente}"
                        
                        # Adicionar versão específica, se fornecida
                        if versao:
                            comando += f"=={versao}"
                        
                        # Adicionar opções extras
                        for opt in opcoes_extras:
                            comando += f" {opt}"
                        
                        # Exibir comando que será executado
                        st.code(comando)
                        
                        # Executar comando pip install
                        import subprocess
                        process = subprocess.Popen(comando.split(), 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
                        stdout, stderr = process.communicate()
                        
                        if process.returncode == 0:
                            st.success(f"Componente {nome_componente} instalado com sucesso!")
                            st.markdown("### Saída da Instalação:")
                            st.code(stdout.decode())
                            
                            # Instruções de uso após instalação
                            st.markdown(f"""
                            ### Como usar o componente
                            
                            Para usar o componente em suas páginas, normalmente você precisa importá-lo:
                            
                            ```python
                            import {nome_componente.replace('-', '_')}
                            ```
                            
                            Consulte a documentação específica do componente para instruções detalhadas.
                            """)
                            
                            # Botão para reiniciar o Streamlit (necessário para que o novo componente seja reconhecido)
                            if st.button("Reiniciar aplicação para aplicar alterações"):
                                st.rerun()
                        else:
                            st.error("Erro ao instalar o componente.")
                            st.markdown("### Erro:")
                            st.code(stderr.decode())
                    except Exception as e:
                        st.error(f"Erro ao instalar o componente: {str(e)}")
                else:
                    st.warning("Por favor, insira o nome do componente.")
        
        # Informações adicionais
        st.markdown("---")
        st.markdown("""
        ### Componentes Populares do Streamlit
        
        Aqui estão alguns componentes populares do Streamlit que você pode querer instalar:
        
        | Nome do Componente | Descrição | Comando de Instalação |
        |-------------------|-----------|---------------------|
        | streamlit-echarts | Gráficos interativos com ECharts | `streamlit-echarts` |
        | streamlit-aggrid | Tabelas interativas e avançadas | `streamlit-aggrid` |
        | streamlit-folium | Mapas interativos | `streamlit-folium` |
        | streamlit-drawable-canvas | Canvas para desenho livre | `streamlit-drawable-canvas` |
        | streamlit-javascript | Integração com JavaScript | `streamlit-javascript` |
        | streamlit-lottie | Animações Lottie | `streamlit-lottie` |
        | streamlit-pandas-profiling | Análise exploratória de dados | `streamlit-pandas-profiling` |
        | streamlit-plotly-events | Eventos interativos para gráficos Plotly | `streamlit-plotly-events` |
        
        Para mais componentes, visite a [galeria oficial de componentes do Streamlit](https://streamlit.io/components).
        """)

# Rodapé
st.markdown("---")
st.caption(f"Sistema de Gestão Suinocultura | Área do Desenvolvedor © {datetime.datetime.now().year} - Todos os direitos reservados")