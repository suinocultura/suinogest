"""
Script para criar um APK usando Buildozer em um serviço online
Este script configura os arquivos necessários para compilar um APK usando serviços online de compilação Buildozer
"""

import os
import sys
import shutil
import json
import tempfile
import logging
import zipfile
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("BuildozerOnline")

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
VERSION = "1.0.0"
URL = "https://workspace.ruanlouco231.repl.co"

def prepare_buildozer_project():
    """Prepara um projeto Buildozer para envio ao serviço de compilação online"""
    # Criar diretório temporário para o projeto
    base_dir = os.path.join(os.getcwd(), "buildozer_project")
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    # Criar main.py (aplicativo Kivy com WebView)
    with open(os.path.join(base_dir, "main.py"), "w") as f:
        f.write(f"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.webview import WebView

class WebViewApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        webview = WebView(url="{URL}")
        layout.add_widget(webview)
        return layout

if __name__ == '__main__':
    WebViewApp().run()
""")
    
    # Criar buildozer.spec
    with open(os.path.join(base_dir, "buildozer.spec"), "w") as f:
        f.write(f"""
[app]
title = {APP_NAME}
package.name = {PACKAGE_NAME}
package.domain = org.test
source.dir = .
source.include_exts = py
version = {VERSION}
requirements = python3,kivy,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 29
android.minapi = 21
android.ndk = 23b
android.sdk = 29
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
""")
    
    # Criar arquivo README com instruções
    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(f"""# Projeto Buildozer - {APP_NAME}

Este projeto está configurado para criar um APK Android usando Buildozer.

## Compilação com Buildozer Serviço Online

1. Faça upload deste projeto para um serviço online como [Buildozer Online](https://buildozer-online.com)
2. Aguarde a compilação (pode levar alguns minutos)
3. Faça o download do APK gerado

## Compilação Local com Buildozer

Se você deseja compilar localmente:

```bash
pip install buildozer
buildozer android debug
```

""")
    
    # Compactar o projeto
    zip_path = os.path.join(os.getcwd(), "buildozer_project.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(base_dir))
                zipf.write(file_path, arcname)
    
    logger.info(f"Projeto Buildozer preparado com sucesso: {zip_path}")
    return zip_path

def create_html_guide():
    """Cria uma página HTML com instruções para usar serviços online de Buildozer"""
    html_path = os.path.join(os.getcwd(), "download_page/buildozer_online_guide.html")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compilação do APK com Buildozer Online - Sistema Suinocultura</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .method {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 15px 0;
        }}
        .button {{
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 15px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin: 10px 0;
        }}
        code {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: monospace;
        }}
        .important {{
            background-color: #ffe6e6;
            border-left: 4px solid #e74c3c;
            padding: 10px;
            margin: 15px 0;
        }}
        .step {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .step-number {{
            display: inline-block;
            width: 30px;
            height: 30px;
            background-color: #3498db;
            color: white;
            text-align: center;
            line-height: 30px;
            border-radius: 50%;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Compilação do APK com Buildozer Online</h1>
        <p>Crie um APK nativo para o Sistema Suinocultura usando o Buildozer em um serviço online.</p>
    </div>

    <div class="container">
        <h2>Método Kivy/Buildozer (Avançado)</h2>
        <p>Este método usa o Kivy framework e Buildozer para criar um APK mais completo e nativo.</p>
        
        <div class="step">
            <span class="step-number">1</span>
            <strong>Baixe o Projeto Buildozer</strong>
            <p>Primeiro, faça o download do projeto preparado para Buildozer:</p>
            <a href="buildozer_project.zip" download class="button">Baixar Projeto Buildozer</a>
        </div>
        
        <div class="step">
            <span class="step-number">2</span>
            <strong>Acesse um Serviço de Compilação Buildozer Online</strong>
            <p>Escolha um dos serviços abaixo:</p>
            <ul>
                <li><a href="https://buildozer-online.com" target="_blank">Buildozer Online</a></li>
                <li><a href="https://buildozer.sagemath.org" target="_blank">Sage Buildozer</a></li>
                <li><a href="https://cocalc.com" target="_blank">CoCalc</a> (selecione "Linux with Kivy")</li>
            </ul>
        </div>
        
        <div class="step">
            <span class="step-number">3</span>
            <strong>Faça Upload do Projeto</strong>
            <p>Após acessar o serviço, faça upload do arquivo <code>buildozer_project.zip</code> que você baixou.</p>
        </div>
        
        <div class="step">
            <span class="step-number">4</span>
            <strong>Inicie a Compilação</strong>
            <p>Siga as instruções do serviço para iniciar a compilação do APK. Em geral, você precisará:</p>
            <ul>
                <li>Extrair o arquivo ZIP</li>
                <li>Executar o comando <code>buildozer android debug</code></li>
                <li>Aguardar a conclusão da compilação (pode levar alguns minutos)</li>
            </ul>
        </div>
        
        <div class="step">
            <span class="step-number">5</span>
            <strong>Baixe o APK</strong>
            <p>Após a conclusão da compilação, o serviço disponibilizará o APK para download. Geralmente, o arquivo estará na pasta <code>bin/</code> do projeto.</p>
        </div>
    </div>

    <div class="container">
        <h2>Método Alternativo: Use CoLab para Compilação</h2>
        <div class="method">
            <h3>Compilar no Google Colab:</h3>
            <p>O Google Colab é uma opção gratuita para compilar seu APK:</p>
            <ol>
                <li>Acesse <a href="https://colab.research.google.com/" target="_blank">Google Colab</a></li>
                <li>Crie um novo notebook</li>
                <li>Copie e cole o seguinte código:</li>
                <pre><code>
# Instalar Buildozer
!pip install buildozer cython==0.29.19

# Instalar dependências
!apt-get update
!apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# Instalar dependências do Buildozer
!apt-get install -y libltdl-dev libffi-dev libssl-dev autoconf automake libtool pkg-config

# Instalar dependências do SDK Android
!apt-get install -y openjdk-8-jdk

# Fazer upload do arquivo ZIP
from google.colab import files
uploaded = files.upload()  # Faça upload do arquivo buildozer_project.zip

# Extrair o projeto
!mkdir -p buildozer_project
!unzip -o buildozer_project.zip -d buildozer_project
%cd buildozer_project

# Compilar o APK
!buildozer android debug

# Fazer download do APK
%cd bin
files.download('*.apk')  # Baixa o APK gerado
                </code></pre>
                <li>Faça upload do arquivo <code>buildozer_project.zip</code> quando solicitado</li>
                <li>Aguarde a compilação e faça o download do APK</li>
            </ol>
            <a href="https://colab.research.google.com/" target="_blank" class="button">Ir para Google Colab</a>
        </div>
    </div>

    <div class="container">
        <div class="important">
            <h3>⚠️ Importante:</h3>
            <p>A compilação com Buildozer requer um ambiente Linux com várias dependências instaladas. Os serviços online facilitam esse processo.</p>
            <p>A compilação pode levar vários minutos, especialmente na primeira vez.</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Guia HTML para Buildozer online criado em: {html_path}")
    return html_path

def main():
    """Função principal"""
    logger.info("=== Preparação do Projeto Buildozer para Compilação Online ===")
    
    # Preparar os arquivos do projeto
    zip_path = prepare_buildozer_project()
    
    # Criar guia HTML
    html_path = create_html_guide()
    
    logger.info("\n=== Processo concluído com sucesso! ===")
    logger.info(f"Projeto Buildozer: {zip_path}")
    logger.info(f"Guia HTML: {html_path}")
    logger.info("\nSiga as instruções no guia HTML para compilar o APK.")

if __name__ == "__main__":
    main()