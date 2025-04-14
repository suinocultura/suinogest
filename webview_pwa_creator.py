#!/usr/bin/env python3
"""
Script para criar um APK PWA (Progressive Web App) a partir de uma URL usando Bubblewrap
Funciona como uma alternativa ao WebView convencional, com melhor integração com o sistema
"""

import os
import sys
import subprocess
import json
import shutil
import time

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
URL = "https://suinocultura.replit.app"
VERSION = "2.1"
VERSION_CODE = 2100
APP_COLOR = "#2196F3"

def check_environment():
    """Verifica se o ambiente tem os requisitos necessários"""
    print("Verificando ambiente...")
    
    # Verificar se está no Termux
    in_termux = "com.termux" in os.environ.get("PREFIX", "")
    if in_termux:
        print("Ambiente Termux detectado.")
    else:
        print("Este script é otimizado para o Termux, mas tentará continuar.")
    
    # Verificar Node.js e npm
    try:
        node_version = subprocess.check_output(["node", "--version"]).decode().strip()
        npm_version = subprocess.check_output(["npm", "--version"]).decode().strip()
        print(f"Node.js: {node_version}, npm: {npm_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Node.js e/ou npm não estão instalados.")
        
        if in_termux:
            print("Instalando Node.js e npm...")
            try:
                subprocess.run(["pkg", "update", "-y"], check=True)
                subprocess.run(["pkg", "install", "-y", "nodejs"], check=True)
                # Verificar novamente
                node_version = subprocess.check_output(["node", "--version"]).decode().strip()
                npm_version = subprocess.check_output(["npm", "--version"]).decode().strip()
                print(f"Node.js: {node_version}, npm: {npm_version}")
            except subprocess.SubprocessError:
                print("Falha ao instalar Node.js e npm. Por favor, instale-os manualmente.")
                return False
        else:
            print("Por favor, instale Node.js e npm manualmente.")
            return False
    
    return True

def install_pwa_builder():
    """Instala o Bubblewrap CLI (pwa-builder)"""
    print("Instalando @pwa-builder/cli...")
    
    try:
        # Verificar se já está instalado
        result = subprocess.run(["npx", "@pwa-builder/cli", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"@pwa-builder/cli já está instalado: {result.stdout.strip()}")
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    try:
        # Instalar globalmente
        subprocess.run(["npm", "install", "-g", "@pwa-builder/cli"], check=True)
        print("@pwa-builder/cli instalado com sucesso.")
        return True
    except subprocess.SubprocessError:
        print("Falha ao instalar @pwa-builder/cli.")
        return False

def create_manifest():
    """Cria o arquivo de manifesto para o PWA"""
    print("Criando manifesto do PWA...")
    
    manifest = {
        "name": APP_NAME,
        "short_name": APP_NAME,
        "start_url": URL,
        "display": "standalone",
        "background_color": APP_COLOR,
        "theme_color": APP_COLOR,
        "icons": [
            {
                "src": "https://via.placeholder.com/192x192?text=Suino",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://via.placeholder.com/512x512?text=Suino",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "related_applications": []
    }
    
    os.makedirs("pwa", exist_ok=True)
    with open("pwa/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print("Manifesto criado: pwa/manifest.json")
    return True

def generate_pwa_assets():
    """Gera os ativos necessários para o PWA"""
    print("Gerando ativos do PWA...")
    
    # Criar HTML simples que redireciona para a URL real
    with open("pwa/index.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{APP_NAME}</title>
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="{APP_COLOR}">
  <style>
    body {{
      margin: 0;
      padding: 0;
      font-family: sans-serif;
      background-color: {APP_COLOR};
      color: white;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 100vh;
      text-align: center;
    }}
    .loader {{
      border: 6px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top: 6px solid white;
      width: 40px;
      height: 40px;
      animation: spin 1.5s linear infinite;
      margin: 20px auto;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
  </style>
  <script>
    window.onload = function() {{
      // Redirecionar para a URL real após um pequeno atraso
      setTimeout(function() {{
        window.location.href = "{URL}";
      }}, 1000);
    }};
  </script>
</head>
<body>
  <h2>{APP_NAME}</h2>
  <div class="loader"></div>
  <p>Carregando sistema...</p>
</body>
</html>""")
    
    print("Arquivo index.html criado")
    return True

def build_apk():
    """Constrói o APK usando o Bubblewrap CLI"""
    print("Construindo APK com PWABuilder... Isso pode levar alguns minutos.")
    
    try:
        # Mudar para o diretório do PWA
        os.chdir("pwa")
        
        # Gerar APK
        subprocess.run([
            "npx", "@pwa-builder/cli", "build", "--androidPackageId", PACKAGE_NAME,
            "--name", APP_NAME, "--appVersionName", VERSION, 
            "--appVersionCode", str(VERSION_CODE), "--manifest", "manifest.json"
        ], check=True)
        
        # Verificar se o APK foi gerado
        apk_path = None
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".apk"):
                    apk_path = os.path.join(root, file)
                    break
            if apk_path:
                break
        
        if apk_path:
            # Copiar para a pasta de downloads
            download_path = os.path.expanduser("~/storage/downloads/SistemaSuinocultura.apk")
            shutil.copy(apk_path, download_path)
            print(f"APK copiado para: {download_path}")
            return True
        else:
            print("APK não foi gerado ou não foi encontrado.")
            return False
    
    except subprocess.SubprocessError as e:
        print(f"Erro ao construir APK: {e}")
        return False
    finally:
        # Voltar ao diretório original
        os.chdir("..")

def alternative_method():
    """Método alternativo usando apenas HTML e um gerador de APK online"""
    print("Preparando método alternativo...")
    
    # Gerar o HTML para uso com um gerador de APK online
    with open("webview_template.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{APP_NAME}</title>
  <style>
    body, html {{
      margin: 0;
      padding: 0;
      height: 100%;
      overflow: hidden;
    }}
    iframe {{
      width: 100%;
      height: 100%;
      border: none;
    }}
  </style>
</head>
<body>
  <iframe src="{URL}" allowfullscreen></iframe>
</body>
</html>""")
    
    print("""
=== Método Alternativo ===
1. Foi gerado um arquivo 'webview_template.html' que você pode usar com serviços online 
   como AppCreator24 ou PWA2APK.

2. Visite um dos seguintes sites em seu navegador:
   - https://appcreator24.com/
   - https://www.pwa2apk.com/
   - https://www.appsgeyser.com/

3. Faça upload do arquivo 'webview_template.html' ou informe diretamente a URL:
   {0}

4. Configure o nome do aplicativo: {1}
   Escolha um ícone adequado

5. Gere o APK e faça o download para o seu dispositivo
""".format(URL, APP_NAME))
    
    return True

def main():
    """Função principal"""
    print("=== Criador de APK PWA para Sistema Suinocultura ===")
    print(f"Aplicativo: {APP_NAME}")
    print(f"URL: {URL}")
    print(f"Versão: {VERSION}")
    print()
    
    # Verificar acesso ao armazenamento (para Termux)
    if "termux" in os.environ.get("PREFIX", "") and not os.path.exists(os.path.expanduser("~/storage")):
        print("Concedendo permissões de armazenamento...")
        try:
            subprocess.run(["termux-setup-storage"], check=True)
            time.sleep(2)  # Aguardar conclusão
        except:
            print("Por favor, execute 'termux-setup-storage' manualmente se estiver usando o Termux")
    
    # Verificar ambiente
    if not check_environment():
        print("O ambiente não atende aos requisitos. Gerando solução alternativa...")
        alternative_method()
        sys.exit(1)
    
    # Instalar ferramentas necessárias
    if not install_pwa_builder():
        print("Não foi possível instalar as ferramentas necessárias. Gerando solução alternativa...")
        alternative_method()
        sys.exit(1)
    
    # Criar manifesto
    if not create_manifest():
        print("Falha ao criar o manifesto. Gerando solução alternativa...")
        alternative_method()
        sys.exit(1)
    
    # Gerar ativos
    if not generate_pwa_assets():
        print("Falha ao gerar os ativos. Gerando solução alternativa...")
        alternative_method()
        sys.exit(1)
    
    # Construir APK
    if build_apk():
        print("=== Processo concluído com sucesso! ===")
        print("O APK está disponível na pasta de downloads: SistemaSuinocultura.apk")
    else:
        print("=== Falha na construção do APK ===")
        print("Gerando método alternativo...")
        alternative_method()

if __name__ == "__main__":
    main()