#!/usr/bin/env python3
"""
Script para criar e compilar um APK WebView diretamente no Replit
Este script configura e compila um APK básico que carrega a aplicação web do Sistema Suinocultura
"""

import os
import sys
import subprocess
import shutil
import zipfile
import logging
import tempfile
import time
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ReplotAPKCreator")

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
VERSION = "1.0.0"
URL = "https://suinocultura.replit.app"
ICON_PATH = "android_app_base/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"

def setup_environment():
    """Configurar ambiente para compilação"""
    logger.info("Configurando ambiente para compilação...")
    
    # Criar diretório de trabalho temporário
    build_dir = os.path.join(os.getcwd(), "apk_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Copiar arquivos base do Android para o diretório de compilação
    android_base_dir = os.path.join(os.getcwd(), "android_app_base")
    if not os.path.exists(android_base_dir):
        logger.error(f"Diretório base do Android não encontrado: {android_base_dir}")
        return False
    
    # Copiar estrutura
    shutil.copytree(android_base_dir, os.path.join(build_dir, "android_app"))
    
    # Atualizar URL no MainActivity.java
    main_activity_path = os.path.join(build_dir, "android_app/app/src/main/java/com/suinocultura/app/MainActivity.java")
    if os.path.exists(main_activity_path):
        with open(main_activity_path, 'r') as f:
            content = f.read()
        
        # Substituir URL
        content = content.replace("https://sua-url-aqui.repl.co", URL)
        content = content.replace("https://sistema-suinocultura.replit.app", URL)
        
        with open(main_activity_path, 'w') as f:
            f.write(content)
    
    logger.info("Ambiente configurado com sucesso!")
    return build_dir

def compile_apk(build_dir):
    """Compilar o APK usando ferramentas online ou Android SDK"""
    logger.info("Preparando arquivos para compilação...")
    
    # Compactar arquivos do projeto Android
    zip_path = os.path.join(os.getcwd(), "android_project.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(os.path.join(build_dir, "android_app")):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)
    
    logger.info(f"Arquivos do projeto compactados em: {zip_path}")
    
    # Instruções para compilação
    logger.info("\nInstruções para compilação do APK:")
    logger.info("1. Faça o download do arquivo android_project.zip")
    logger.info("2. Acesse um serviço online de compilação de APK como AppInventor ou Thunkable")
    logger.info("3. Faça upload do projeto ou use um dos seguintes serviços:")
    logger.info("   - BuildAPK Online: https://www.buildapk.online/")
    logger.info("   - APK Builder: https://apkbuilder.net/")
    logger.info("   - AppMakr: https://www.appmakr.com/")
    logger.info(f"4. Configure a URL do WebView como: {URL}")
    logger.info("5. Faça o download do APK compilado\n")
    
    return zip_path

def create_apk_webview_html():
    """Criar um arquivo HTML para geração de APK online"""
    html_path = os.path.join(os.getcwd(), "download_page/apk_webview_creator.html")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Criador de APK - Sistema Suinocultura</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Criador de APK - Sistema Suinocultura</h1>
        <p>Use este aplicativo para acessar o Sistema de Gestão Suinocultura de qualquer dispositivo Android.</p>
    </div>

    <div class="container">
        <h2>Método 1: APK Online Builder (Mais Fácil)</h2>
        <div class="method">
            <h3>Passos:</h3>
            <ol>
                <li>Acesse <a href="https://gonative.io/app/free" target="_blank">GoNative.io</a> (criador de APK grátis)</li>
                <li>Digite a URL: <code>{URL}</code></li>
                <li>Digite o nome do app: <code>{APP_NAME}</code></li>
                <li>Complete as informações adicionais</li>
                <li>Clique em "Build My App" e faça o download do APK</li>
            </ol>
            <a href="https://gonative.io/app/free" target="_blank" class="button">Ir para GoNative.io</a>
        </div>
    </div>

    <div class="container">
        <h2>Método 2: WebViewGold</h2>
        <div class="method">
            <h3>Passos:</h3>
            <ol>
                <li>Acesse <a href="https://webviewgold.com/generate/" target="_blank">WebViewGold</a></li>
                <li>Digite a URL: <code>{URL}</code></li>
                <li>Complete o restante do formulário</li>
                <li>Faça o download do APK gerado</li>
            </ol>
            <a href="https://webviewgold.com/generate/" target="_blank" class="button">Ir para WebViewGold</a>
        </div>
    </div>

    <div class="container">
        <h2>Método 3: AppyBuilder</h2>
        <div class="method">
            <h3>Passos:</h3>
            <ol>
                <li>Acesse <a href="https://appybuilder.com/" target="_blank">AppyBuilder</a></li>
                <li>Crie uma conta gratuita</li>
                <li>Crie um novo projeto do tipo "WebView"</li>
                <li>Configure a URL: <code>{URL}</code></li>
                <li>Exporte o APK</li>
            </ol>
            <a href="https://appybuilder.com/" target="_blank" class="button">Ir para AppyBuilder</a>
        </div>
    </div>

    <div class="container">
        <div class="important">
            <h3>⚠️ Importante:</h3>
            <p>Depois de instalar o APK, talvez seja necessário conceder permissões adicionais de "instalar de fontes desconhecidas" no seu dispositivo.</p>
            <p>Este APK é apenas um "wrapper" (invólucro) para o site do Sistema Suinocultura e requer conexão com a internet para funcionar.</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Arquivo HTML para criação de APK online criado em: {html_path}")
    return html_path

def main():
    """Função principal"""
    logger.info("=== Criador de APK WebView para Sistema Suinocultura ===")
    logger.info(f"Aplicativo: {APP_NAME}")
    logger.info(f"URL: {URL}")
    logger.info(f"Versão: {VERSION}")
    
    # Configurar ambiente
    build_dir = setup_environment()
    if not build_dir:
        logger.error("Falha ao configurar o ambiente.")
        sys.exit(1)
    
    # Compilar APK (ou preparar arquivos para compilação)
    zip_path = compile_apk(build_dir)
    
    # Criar HTML para geração de APK online
    html_path = create_apk_webview_html()
    
    logger.info("\n=== Processo concluído com sucesso! ===")
    logger.info(f"Projeto Android disponível em: {zip_path}")
    logger.info(f"Página HTML para criação de APK: {html_path}")
    logger.info("\nBaixe estes arquivos e siga as instruções para criar seu APK.")

if __name__ == "__main__":
    main()