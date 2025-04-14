#!/usr/bin/env python3
"""
Script para criar uma aplicação WebView simples usando a biblioteca pybrowserapp
Esta é uma versão mais simples que não requer o ambiente completo do Kivy
"""

import os
import sys
import subprocess
import json
import time

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
URL = "https://workspace.ruanlouco231.repl.co"
VERSION = "2.1"

def check_dependencies():
    """Verifica e instala as dependências necessárias"""
    try:
        import pybrowserapp
        print("A biblioteca pybrowserapp já está instalada.")
        return True
    except ImportError:
        print("Instalando pybrowserapp...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pybrowserapp"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("Falha ao instalar pybrowserapp. Verifique sua conexão com a internet.")
            return False

def create_app_config():
    """Cria o arquivo de configuração para o aplicativo"""
    print("Criando configuração do aplicativo...")
    config = {
        "app_name": APP_NAME,
        "package_name": PACKAGE_NAME,
        "version": VERSION,
        "url": URL,
        "orientation": "portrait",
        "permissions": ["INTERNET", "ACCESS_NETWORK_STATE"],
        "show_navigation_buttons": True,
        "fullscreen": False,
        "status_bar_color": "#2196F3",
        "theme_color": "#2196F3",
        "splash_screen_delay": 1000,
        "user_agent": "Android WebView"
    }
    
    with open("app_config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("Arquivo de configuração criado: app_config.json")
    return True

def build_apk():
    """Constrói o APK usando pybrowserapp"""
    print("Construindo APK... Isso pode levar alguns minutos.")
    
    try:
        from pybrowserapp import WebViewApp
        app = WebViewApp("app_config.json")
        apk_path = app.build(debug=True)
        
        print(f"APK criado com sucesso: {apk_path}")
        
        # Copiar para pasta de downloads
        download_path = os.path.expanduser("~/storage/downloads/SistemaSuinocultura.apk")
        import shutil
        shutil.copy(apk_path, download_path)
        print(f"APK copiado para: {download_path}")
        return True
    
    except Exception as e:
        print(f"Erro ao construir APK: {e}")
        return False

def main():
    """Função principal"""
    print("=== Criador de APK WebView Simples para Sistema Suinocultura ===")
    print(f"Aplicativo: {APP_NAME}")
    print(f"URL: {URL}")
    print(f"Versão: {VERSION}")
    print()
    
    # Verificar se está em um ambiente apropriado
    if "termux" not in os.environ.get("PREFIX", "") and not os.path.exists("/data/data/com.termux"):
        print("Aviso: Este script funciona melhor no Termux ou Pydroid 3.")
    
    # Verificar acesso ao armazenamento
    if not os.path.exists(os.path.expanduser("~/storage")) and "termux" in os.environ.get("PREFIX", ""):
        print("Concedendo permissões de armazenamento...")
        try:
            subprocess.run(["termux-setup-storage"], check=True)
            time.sleep(2)  # Aguardar conclusão
        except:
            print("Por favor, execute 'termux-setup-storage' manualmente se estiver usando o Termux")
    
    # Verificar e instalar dependências
    if not check_dependencies():
        print("Não foi possível instalar as dependências necessárias.")
        sys.exit(1)
    
    # Criar configuração
    if not create_app_config():
        print("Falha ao criar a configuração do aplicativo.")
        sys.exit(1)
    
    # Construir APK
    if build_apk():
        print("=== Processo concluído com sucesso! ===")
        print("O APK está disponível na pasta de downloads.")
    else:
        print("=== Falha na construção do APK ===")
        print("Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()