#!/usr/bin/env python3
"""
Script para criar uma aplicação Android WebView simples que carrega uma URL
Usando abordagem baseada em WebView nativo do Android
"""

import os
import sys
import shutil
import zipfile
import json
import subprocess
import tempfile
from pathlib import Path
import time

# Configurações do aplicativo
APP_NAME = "Sistema Suinocultura"
PACKAGE_NAME = "com.suinocultura.app"
URL = "https://suinocultura.replit.app"
VERSION = "2.1"
VERSION_CODE = 210

def create_project_structure():
    """Cria a estrutura de diretórios do projeto Android"""
    print("Criando estrutura do projeto Android...")
    base_dir = "android_webview_project"
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(base_dir)
    os.chdir(base_dir)
    
    # Criar estrutura básica
    os.makedirs("app/src/main/java/com/suinocultura/app", exist_ok=True)
    os.makedirs("app/src/main/res/layout", exist_ok=True)
    os.makedirs("app/src/main/res/values", exist_ok=True)
    os.makedirs("app/src/main/res/drawable", exist_ok=True)
    os.makedirs("app/src/main/res/mipmap/ic_launcher", exist_ok=True)
    
    return base_dir

def create_manifest():
    """Cria o Android Manifest"""
    print("Criando AndroidManifest.xml...")
    manifest_path = "app/src/main/AndroidManifest.xml"
    
    with open(manifest_path, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{PACKAGE_NAME}"
    android:versionCode="{VERSION_CODE}"
    android:versionName="{VERSION}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@android:style/Theme.NoTitleBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|keyboardHidden|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
""")

def create_main_activity():
    """Cria o arquivo MainActivity.java"""
    print("Criando MainActivity.java...")
    activity_path = "app/src/main/java/com/suinocultura/app/MainActivity.java"
    
    with open(activity_path, "w") as f:
        f.write(f"""package {PACKAGE_NAME};

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.KeyEvent;
import android.widget.Toast;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.content.Context;

public class MainActivity extends Activity {{

    private WebView webView;
    private static final String STREAMLIT_URL = "{URL}";
    private long backPressedTime = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = (WebView) findViewById(R.id.webView);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Habilitar cache para funcionamento offline limitado
        webSettings.setAppCacheEnabled(true);
        String appCachePath = getApplicationContext().getCacheDir().getAbsolutePath();
        webSettings.setAppCachePath(appCachePath);
        
        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {{
                if (!isNetworkAvailable()) {{
                    Toast.makeText(MainActivity.this, "Sem conexão com a internet. Algumas funcionalidades podem não estar disponíveis.", Toast.LENGTH_LONG).show();
                }}
            }}
            
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {{
                view.loadUrl(url);
                return true;
            }}
        }});

        if (isNetworkAvailable()) {{
            webView.loadUrl(STREAMLIT_URL);
        }} else {{
            Toast.makeText(this, "Sem conexão com a internet. Algumas funcionalidades podem não estar disponíveis.", Toast.LENGTH_LONG).show();
            webView.loadUrl(STREAMLIT_URL); // Tenta carregar mesmo assim, pode usar cache
        }}
    }}

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {{
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {{
            webView.goBack();
            return true;
        }}
        
        if (keyCode == KeyEvent.KEYCODE_BACK && !webView.canGoBack()) {{
            if (backPressedTime + 2000 > System.currentTimeMillis()) {{
                finish();
                return true;
            }} else {{
                Toast.makeText(this, "Pressione voltar novamente para sair", Toast.LENGTH_SHORT).show();
                backPressedTime = System.currentTimeMillis();
                return true;
            }}
        }}
        
        return super.onKeyDown(keyCode, event);
    }}
    
    private boolean isNetworkAvailable() {{
        ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
        return activeNetworkInfo != null && activeNetworkInfo.isConnected();
    }}
}}
""")

def create_layout():
    """Cria o arquivo de layout"""
    print("Criando layout XML...")
    layout_path = "app/src/main/res/layout/activity_main.xml"
    
    with open(layout_path, "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</RelativeLayout>
""")

def create_strings():
    """Cria o arquivo de strings"""
    print("Criando arquivo de strings...")
    strings_path = "app/src/main/res/values/strings.xml"
    
    with open(strings_path, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{APP_NAME}</string>
</resources>
""")

def create_colors():
    """Cria o arquivo de cores"""
    print("Criando arquivo de cores...")
    colors_path = "app/src/main/res/values/colors.xml"
    
    with open(colors_path, "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#4CAF50</color>
    <color name="colorPrimaryDark">#388E3C</color>
    <color name="colorAccent">#FF9800</color>
</resources>
""")

def create_build_gradle():
    """Cria os arquivos build.gradle"""
    print("Criando arquivos build.gradle...")
    
    # Arquivo build.gradle raiz
    with open("build.gradle", "w") as f:
        f.write("""buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.2.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
""")
    
    # Arquivo build.gradle do app
    with open("app/build.gradle", "w") as f:
        f.write(f"""plugins {{
    id 'com.android.application'
}}

android {{
    compileSdkVersion 32
    defaultConfig {{
        applicationId "{PACKAGE_NAME}"
        minSdkVersion 21
        targetSdkVersion 32
        versionCode {VERSION_CODE}
        versionName "{VERSION}"
    }}
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.5.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}}
""")

def create_gradle_wrapper():
    """Cria os arquivos do Gradle Wrapper"""
    print("Criando Gradle Wrapper...")
    
    os.makedirs("gradle/wrapper", exist_ok=True)
    
    # gradle-wrapper.properties
    with open("gradle/wrapper/gradle-wrapper.properties", "w") as f:
        f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-7.3.3-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""")
    
    # gradlew script
    with open("gradlew", "w") as f:
        f.write("""#!/usr/bin/env sh
# Gradle startup script for Unix
""")
    
    # gradlew.bat script
    with open("gradlew.bat", "w") as f:
        f.write("""@rem Gradle startup script for Windows
@rem
""")

def create_settings_gradle():
    """Cria o arquivo settings.gradle"""
    print("Criando settings.gradle...")
    
    with open("settings.gradle", "w") as f:
        f.write("""include ':app'
rootProject.name = "SistemaSuinocultura"
""")

def create_icon():
    """Cria um ícone simples para o app"""
    print("Criando ícone básico...")
    
    # Arquivo ícone
    with open("app/src/main/res/mipmap/ic_launcher/ic_launcher.png", "wb") as f:
        # Bytes para um ícone básico de 192x192 pixels
        # Este é um truque para não depender de bibliotecas de imagem
        # Em um cenário real, você usaria um ícone verdadeiro
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x06bKGD\x00\xff\x00\xff\x00\xff\xa0\xbd\xa7\x93\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe0\x01\x1f\x02\x12\x05\xfd\xb4\x9a\xa8\x00\x00\x00\x1diTXtComment\x00\x00\x00\x00\x00Created with GIMPd.e\x07\x00\x00\x01}IDATX\xc3\xed\x96\xbfJ\x03A\x10\x87\xbf\x13\xb5\x08h!\x12D\x88\x85Z(XY\xe9\x03\xf8\x06\n\x82+bk\x1f\xc0G\xb0\x14\xc4\xda\'\xb0\xf2\rRY\x88`\x11\x0b\x1b\x11\x0bE\x10\xb4P\xc4\xe2\xb2\x1f\xc5\xdc\x91\'g\xee.\x17\x043\xb0\xc5\xc2\xcc\xec\xef\xdb\xbf\x0b+d\x99\x05(h\x00\x17\xa6e\xf6CW\x9b\x05\xdcz\xe7J3`\x0b\xc8u\xa9\x18\x03\x1e\x80\x06\xf0\xd4\t\xde\x18\x80\xdf\xad\xc3\xb4D*\xc0\x9c\xc7\x9c\x8c\x81\x1b\xe0\xcd\x00\xf4}\x00\xf2\xc0\xae\xc7\x1c0\x01\xb6\x81\xd3\xb4\xbc\x1f\x02\xfbQR\x1d8\xca\x80.^\x02+I\xb9\x9d\x06\xc0\x8d\xac\x01\x8b\xc0#\xb09\x03\xe8\x15\xb0\x91\xb4\xca\x14`B\xb4\xb2\x06\xa0\x1a\xa8\xaepd\n!\xb3\xf69\x07\x1c\xceP\xe4\xf6\x80\xe5_\x15a\x02\xdc\x03\x1f\xc0}@\xd5\x83I\xee\x87\x80\xd1T|T\xa5\xad\xcc\xcf\x01W\x1aQE\xce(\xfd\x8f\xc0\x8a\xc6\xd5\xdb \xfaO\xee\x95\xe7\xbd\x8aR\xd0X\x9c\x02\xce\x81\xe3\x80\xae\x8e\x80\xf3\xd8WN\xa2\xa0V|\x00N\x02\xba\xaa\x02\xd7\x16\xc0\x06\xb0\x96*\x93\x95"\xef\x15\xbd<z\x9f\xd6b\x19\xd8\x8f]\xd5\x11\x13\xf1\x03+@\xd1\xd3HF\xc0k&AiP\x9d\xf5\xfd\x17\x0c\xa6\x14\xd9\xf0\x94k\tXw\x9cX\xd6\xc6\xad\x89\xd0\x8b\x01\xd2^z\t\xad\xfb\x03\x88\xe46\x10\xa4\x80o\x1d\xa7\x91\xe3>\x14]\x00\x00\x00\x00IEND\xaeB`\x82')

def create_online_apk_guide():
    """Criar uma página HTML com instruções para compilação online"""
    print("Criando guia para compilação online...")
    
    html_path = "../../online_apk_creation_guide.html"
    
    with open(html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Criação de APK Online - Sistema Suinocultura</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2E7D32;
            text-align: center;
            border-bottom: 2px solid #2E7D32;
            padding-bottom: 10px;
        }}
        .container {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
            background-color: #f9f9f9;
        }}
        ol {{
            margin-left: 20px;
        }}
        .button {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .highlight {{
            background-color: #FFEB3B;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        .card {{
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
        }}
        .note {{
            background-color: #E3F2FD;
            border-left: 4px solid #2196F3;
            padding: 10px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <h1>Criação de APK Online - Sistema Suinocultura</h1>
    
    <div class="container">
        <h2>Sobre este Guia</h2>
        <p>
            Este guia mostra como criar um APK Android para o Sistema Suinocultura usando 
            serviços de compilação online, sem necessidade de instalar Android Studio ou 
            ferramentas de desenvolvimento complexas.
        </p>
        <p>
            O APK gerado será um aplicativo WebView que carrega o Sistema Suinocultura 
            hospedado em <span class="highlight">{URL}</span>.
        </p>
    </div>
    
    <div class="container">
        <h2>Opção 1: Usar um Gerador de APK Online</h2>
        <p>Este é o método mais simples e rápido.</p>
        
        <div class="card">
            <h3>Passo 1: Acesse um serviço de criação de APK WebView</h3>
            <p>Existem vários serviços gratuitos que permitem criar APKs WebView:</p>
            <ul>
                <li><a href="https://gonative.io/free-app" target="_blank">GoNative.io</a> (recomendado)</li>
                <li><a href="https://appsgeyser.com/create/webview/" target="_blank">AppsGeyser</a></li>
                <li><a href="https://www.appybuilder.com/" target="_blank">AppyBuilder</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Passo 2: Configure o aplicativo</h3>
            <p>Preencha os campos necessários:</p>
            <ul>
                <li><strong>Nome do Aplicativo:</strong> Sistema Suinocultura</li>
                <li><strong>URL:</strong> {URL}</li>
                <li><strong>Ícone:</strong> Faça upload de um ícone (ou use o fornecido pelo serviço)</li>
                <li><strong>Cor do tema:</strong> #4CAF50 (verde) ou sua preferência</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Passo 3: Gere e baixe o APK</h3>
            <p>Clique em "Criar APK" ou equivalente e baixe o arquivo quando estiver pronto.</p>
        </div>
    </div>
    
    <div class="container">
        <h2>Opção 2: Usar o Arquivo do Projeto</h2>
        <p>Este método permite mais personalização, mas requer o upload de um arquivo ZIP.</p>
        
        <div class="card">
            <h3>Passo 1: Baixe o arquivo do projeto Android</h3>
            <p>
                Clique no botão abaixo para baixar o arquivo ZIP com o projeto Android completo:
            </p>
            <p>
                <a href="#" class="button" onclick="alert('O arquivo seria baixado aqui. Na versão real, este botão terá o download.')">
                    Baixar Projeto Android WebView
                </a>
            </p>
        </div>
        
        <div class="card">
            <h3>Passo 2: Acesse um serviço de compilação de APK</h3>
            <p>Visite um dos seguintes serviços de compilação de APK online:</p>
            <ul>
                <li><a href="https://www.apkonline.net/" target="_blank">APK Online</a></li>
                <li><a href="https://appsgeyser.com/create/webview/" target="_blank">AppsGeyser</a></li>
                <li><a href="https://www.buildapk.online/" target="_blank">BuildAPK Online</a></li>
            </ul>
        </div>
        
        <div class="card">
            <h3>Passo 3: Faça o upload do arquivo ZIP e compile</h3>
            <p>
                Faça o upload do arquivo ZIP baixado e siga as instruções para compilar o APK.
                O processo pode levar alguns minutos.
            </p>
        </div>
        
        <div class="card">
            <h3>Passo 4: Baixe o APK compilado</h3>
            <p>
                Quando a compilação for concluída, baixe o arquivo APK para seu dispositivo.
            </p>
        </div>
    </div>
    
    <div class="note">
        <h3>Nota importante</h3>
        <p>
            Para instalar o APK, você precisará habilitar "Fontes desconhecidas" nas configurações 
            de segurança do seu dispositivo Android.
        </p>
        <p>
            O aplicativo requer acesso à internet para funcionar corretamente, já que ele 
            carrega o Sistema Suinocultura hospedado online.
        </p>
    </div>
    
    <p style="text-align: center; margin-top: 30px; color: #777;">
        Sistema de Gestão Suinocultura v{VERSION} &copy; 2025
    </p>
</body>
</html>
""")
    
    return html_path

def create_project_zip():
    """Criar um ZIP do projeto para compilação online"""
    print("Criando arquivo ZIP do projeto Android...")
    
    # Retornar ao diretório original
    os.chdir("..")
    
    # Caminho do arquivo ZIP
    zip_path = f"android_webview_project_{VERSION.replace('.', '_')}.zip"
    
    # Criar o arquivo ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("android_webview_project"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)
    
    print(f"Arquivo ZIP criado em: {zip_path}")
    
    return zip_path

def create_direct_apk_alternative():
    """Criar uma alternativa direta para geração de APK"""
    print("Preparando alternativa para geração direta de APK...")
    
    apk_html_path = "direct_apk_creator.html"
    
    with open(apk_html_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerador de APK WebView - Sistema Suinocultura</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
            margin-top: 20px;
        }}
        h1 {{
            color: #2E7D32;
            text-align: center;
            border-bottom: 2px solid #2E7D32;
            padding-bottom: 10px;
        }}
        .btn {{
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }}
        .input-group {{
            margin-bottom: 15px;
        }}
        .input-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        .input-group input, .input-group select {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gerador de APK WebView - Sistema Suinocultura</h1>
        <p>Use este formulário para gerar um APK do Sistema Suinocultura. O APK será criado usando o serviço APK WebView Creator.</p>
        
        <form action="https://gonative.io/free-app" method="get" target="_blank">
            <input type="hidden" name="url" value="{URL}">
            
            <div class="input-group">
                <label for="appName">Nome do aplicativo:</label>
                <input type="text" id="appName" name="appName" value="Sistema Suinocultura" readonly>
            </div>
            
            <div class="input-group">
                <label for="appIcon">Ícone do aplicativo:</label>
                <select id="appIcon" name="appIcon">
                    <option value="default" selected>Usar ícone padrão</option>
                    <option value="custom">Fazer upload de ícone personalizado</option>
                </select>
            </div>
            
            <div class="input-group">
                <label for="theme">Cor do tema:</label>
                <input type="color" id="theme" name="theme" value="#4CAF50">
            </div>
            
            <button type="submit" class="btn">Criar APK WebView Agora</button>
        </form>
        
        <div style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
            <h3>Instruções:</h3>
            <ol>
                <li>Clique no botão "Criar APK WebView Agora"</li>
                <li>Você será redirecionado para um serviço de criação de APK</li>
                <li>Complete quaisquer etapas adicionais exigidas pelo serviço</li>
                <li>Baixe o APK quando estiver pronto</li>
                <li>Instale o APK em seu dispositivo Android</li>
            </ol>
            <p><strong>Nota:</strong> Para instalar o APK, você precisará habilitar "Fontes desconhecidas" nas configurações de segurança do seu dispositivo Android.</p>
        </div>
    </div>
</body>
</html>
""")
    
    return apk_html_path

def main():
    """Função principal"""
    print("=== Criador de APK WebView Simplificado para Sistema Suinocultura ===")
    print(f"Aplicativo: {APP_NAME}")
    print(f"URL: {URL}")
    print(f"Versão: {VERSION}")
    print()
    
    # Verificar ambiente Android
    print("Este script criará os arquivos necessários para compilar um APK WebView.")
    print("Como não podemos compilar diretamente, serão fornecidas alternativas:")
    print("1. Um projeto Android completo que pode ser compilado online")
    print("2. Um guia para usar serviços de compilação online")
    print()
    
    # Criar projeto Android
    create_project_structure()
    
    # Criar arquivos do projeto
    create_manifest()
    create_main_activity()
    create_layout()
    create_strings()
    create_colors()
    create_build_gradle()
    create_gradle_wrapper()
    create_settings_gradle()
    create_icon()
    
    # Criar ZIP do projeto
    zip_path = create_project_zip()
    
    # Criar guia de compilação online
    html_guide_path = create_online_apk_guide()
    
    # Criar alternativa direta
    direct_apk_path = create_direct_apk_alternative()
    
    print("\n=== Processo concluído com sucesso! ===")
    print(f"1. Projeto Android: {zip_path}")
    print(f"2. Guia de compilação online: {html_guide_path}")
    print(f"3. Criador direto de APK: {direct_apk_path}")
    print("\nUse estes arquivos para criar seu APK Android sem precisar do Kivy ou Buildozer.")

if __name__ == "__main__":
    main()