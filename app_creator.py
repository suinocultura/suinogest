#!/usr/bin/env python3
"""
Script para criar uma aplicação Android WebView simples que carrega uma URL
Baseado no Kivy e Buildozer
"""

import os
import sys
import shutil
import subprocess
import time

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
URL = "https://workspace.ruanlouco231.repl.co"
VERSION = "2.1"
APP_ICON = None  # Será gerado automaticamente

def create_app_directory():
    """Cria o diretório para o aplicativo"""
    print("Criando diretório do aplicativo...")
    if os.path.exists("webview_app"):
        shutil.rmtree("webview_app")
    os.makedirs("webview_app")
    os.chdir("webview_app")

def create_main_py():
    """Cria o arquivo main.py do aplicativo"""
    print("Criando arquivo main.py...")
    with open("main.py", "w") as f:
        f.write("""
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.garden.webview import WebView
from kivy.utils import platform

# URL da sua aplicação Streamlit
STREAMLIT_URL = "{}"

class WebViewApp(App):
    def build(self):
        # Layout principal
        layout = BoxLayout(orientation='vertical')
        
        # WebView para carregar a URL
        self.webview = WebView(url=STREAMLIT_URL)
        layout.add_widget(self.webview)
        
        # Layout para botões na parte inferior
        bottom_layout = BoxLayout(size_hint_y=None, height='48dp')
        
        # Botão voltar
        back_button = Button(text='Voltar', size_hint_x=0.25)
        back_button.bind(on_press=self.go_back)
        bottom_layout.add_widget(back_button)
        
        # Botão recarregar
        reload_button = Button(text='Recarregar', size_hint_x=0.25)
        reload_button.bind(on_press=self.reload)
        bottom_layout.add_widget(reload_button)
        
        # Botão avançar
        forward_button = Button(text='Avançar', size_hint_x=0.25)
        forward_button.bind(on_press=self.go_forward)
        bottom_layout.add_widget(forward_button)
        
        # Botão home
        home_button = Button(text='Início', size_hint_x=0.25)
        home_button.bind(on_press=self.go_home)
        bottom_layout.add_widget(home_button)
        
        layout.add_widget(bottom_layout)
        
        # Iniciar o carregamento da URL após um pequeno delay
        Clock.schedule_once(self.load_url, 1)
        
        return layout
    
    def load_url(self, dt):
        self.webview.url = STREAMLIT_URL

    def go_back(self, instance):
        if self.webview.can_go_back():
            self.webview.go_back()

    def go_forward(self, instance):
        if self.webview.can_go_forward():
            self.webview.go_forward()

    def reload(self, instance):
        self.webview.reload()

    def go_home(self, instance):
        self.webview.url = STREAMLIT_URL

if __name__ == '__main__':
    WebViewApp().run()
""".format(URL))

def create_buildozer_spec():
    """Cria o arquivo buildozer.spec"""
    print("Criando arquivo buildozer.spec...")
    with open("buildozer.spec", "w") as f:
        f.write("""
[app]
title = {}
package.name = {}
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = {}
requirements = python3,kivy,android,certifi,garden.webview
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = arm64-v8a
android.accept_sdk_license = True
p4a.bootstrap = sdl2
p4a.branch = master
p4a.hook = 

[buildozer]
log_level = 2
warn_on_root = 1
""".format(APP_NAME, PACKAGE_NAME, VERSION))

def install_dependencies():
    """Instala as dependências necessárias no Termux"""
    print("Instalando dependências no Termux...")
    try:
        print("Atualizando pacotes...")
        subprocess.run(["pkg", "update", "-y"], check=True)
        
        print("Instalando pacotes básicos...")
        packages = ["python", "autoconf", "automake", "libtool", "cmake", 
                    "wget", "git", "build-essential", "python-dev", "libffi-dev"]
        for pkg in packages:
            print(f"Instalando {pkg}...")
            try:
                subprocess.run(["pkg", "install", "-y", pkg], check=True)
            except subprocess.CalledProcessError:
                print(f"Aviso: Falha ao instalar {pkg}, continuando...")
        
        print("Instalando Cython e Buildozer...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "cython"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "buildozer"], check=True)
        
        print("Inicializando Buildozer...")
        if not os.path.exists('buildozer.spec'):
            subprocess.run(["buildozer", "init"], input=b'y\n', check=True)
        
        print("Instalando garden.webview...")
        subprocess.run([sys.executable, "-m", "pip", "install", "kivy-garden"], check=True)
        try:
            subprocess.run(["garden", "install", "webview"], check=True)
        except subprocess.CalledProcessError:
            try:
                subprocess.run([sys.executable, "-m", "kivy.garden", "install", "webview"], check=True)
            except subprocess.CalledProcessError:
                print("Aviso: Não foi possível instalar webview pelo garden, continuando...")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        print("Você pode precisar instalar manualmente:")
        print("pkg install python autoconf automake libtool cmake wget git build-essential")
        print("pip install cython buildozer")
        return False

def compile_apk():
    """Compila o APK usando Buildozer"""
    print("Compilando APK... (isso pode levar vários minutos)")
    print("AVISO: Este processo requer pelo menos 2GB de espaço livre e consome muitos recursos.")
    print("Se o seu dispositivo tiver pouca memória, o processo pode falhar.")
    
    try:
        # Verificar espaço em disco
        import shutil
        total, used, free = shutil.disk_usage("/data")
        free_gb = free / (1024**3)  # Converter para GB
        print(f"Espaço livre disponível: {free_gb:.2f} GB")
        
        if free_gb < 2.0:
            print("AVISO: Você tem menos de 2GB de espaço livre. O processo pode falhar.")
            input("Pressione ENTER para continuar mesmo assim, ou CTRL+C para cancelar...")
        
        # Tentar compilar com diferentes configurações, começando com a mais simples
        try:
            print("Tentativa 1: Compilando versão básica...")
            subprocess.run(["buildozer", "-v", "android", "debug"], check=True, timeout=1800)  # 30 min timeout
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            print(f"Primeira tentativa falhou: {e}")
            print("Tentativa 2: Ajustando configurações e tentando novamente...")
            
            # Modificar buildozer.spec para usar configurações mais simples
            if os.path.exists("buildozer.spec"):
                with open("buildozer.spec", "r") as f:
                    spec = f.read()
                
                # Simplificar requisitos
                spec = spec.replace("requirements = python3,kivy,android,certifi,garden.webview", 
                                   "requirements = python3,kivy,android")
                
                # Reduzir API alvo
                spec = spec.replace("android.api = 31", "android.api = 29")
                spec = spec.replace("android.sdk = 31", "android.sdk = 29")
                
                with open("buildozer.spec", "w") as f:
                    f.write(spec)
            
            try:
                subprocess.run(["buildozer", "-v", "android", "debug"], check=True, timeout=1800)
            except Exception as e2:
                print(f"Segunda tentativa falhou: {e2}")
                print("Criando versão simplificada final...")
                
                # Criar um método ainda mais simples (última tentativa)
                with open("main.py", "w") as f:
                    f.write(f"""
from kivy.app import App
from kivy.uix.webview import WebView
from kivy.uix.boxlayout import BoxLayout

class SimpleWebViewApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        webview = WebView(url="{URL}")
        layout.add_widget(webview)
        return layout

if __name__ == '__main__':
    SimpleWebViewApp().run()
""")
                
                with open("buildozer.spec", "w") as f:
                    f.write(f"""
[app]
title = {APP_NAME}
package.name = {PACKAGE_NAME}
package.domain = org.test
source.dir = .
source.include_exts = py
version = {VERSION}
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 28
android.minapi = 21
android.ndk = 23b
android.sdk = 28
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
""")
                
                subprocess.run(["buildozer", "-v", "android", "debug"], check=True, timeout=1800)
        
        # Verificar se o APK foi criado
        apk_path = None
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".apk"):
                    apk_path = os.path.join(root, file)
                    break
            if apk_path:
                break
        
        if apk_path:
            print(f"APK criado com sucesso: {apk_path}")
            # Copiar para um local acessível
            destination = os.path.expanduser("~/storage/downloads/SistemaSuinocultura.apk")
            shutil.copy(apk_path, destination)
            print(f"APK copiado para: {destination}")
            return True
        else:
            print("APK não foi criado.")
            return False
            
    except Exception as e:
        print(f"Erro ao compilar APK: {e}")
        print("\nSe o processo falhou, você pode tentar o método alternativo mais simples:")
        print("1. Instale o aplicativo 'WebView Creator' da Play Store")
        print(f"2. Configure o URL: {URL}")
        print("3. Configure o nome: Sistema Suinocultura")
        return False

def main():
    """Função principal"""
    print("=== Criador de APK WebView para Sistema Suinocultura ===")
    print(f"Aplicativo: {APP_NAME}")
    print(f"URL: {URL}")
    print(f"Versão: {VERSION}")
    print()
    
    # Verificar ambiente (deve ser Termux)
    if "com.termux" not in os.environ.get("PREFIX", ""):
        print("Este script deve ser executado no Termux!")
        print("Por favor, instale o Termux e execute este script novamente.")
        sys.exit(1)
    
    # Verificar permissões de armazenamento
    if not os.path.exists(os.path.expanduser("~/storage")):
        print("Concedendo permissões de armazenamento...")
        try:
            subprocess.run(["termux-setup-storage"], check=True)
            time.sleep(2)  # Aguardar conclusão
        except:
            print("Falha ao obter permissões. Por favor, execute 'termux-setup-storage' manualmente.")
            sys.exit(1)
    
    # Criar diretório e arquivos do aplicativo
    create_app_directory()
    create_main_py()
    create_buildozer_spec()
    
    # Instalar dependências
    if not install_dependencies():
        print("Falha ao instalar dependências.")
        sys.exit(1)
    
    # Compilar o APK
    if compile_apk():
        print("=== Processo concluído com sucesso! ===")
        print("O APK está disponível em ~/storage/downloads/SistemaSuinocultura.apk")
    else:
        print("=== Falha na compilação do APK ===")
        print("Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()