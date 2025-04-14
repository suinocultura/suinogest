const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');

// Cria pasta build se não existir
if (!fs.existsSync('build')) {
    fs.mkdirSync('build');
}

// Função para baixar o APK
function downloadAPK() {
    console.log('Tentando baixar o APK...');
    
    const file = fs.createWriteStream('build/suinocultura.apk');
    const request = https.get('https://suinocultura.replit.app/download/suinocultura.apk', function(response) {
        if (response.statusCode !== 200) {
            console.log('APK não encontrado. Criando arquivo de espaço reservado.');
            // Cria um arquivo de texto como espaço reservado
            fs.writeFileSync('build/suinocultura.apk', 'Este é um arquivo de espaço reservado para o APK. O aplicativo real pode ser baixado em https://suinocultura.replit.app/pages/99_%F0%9F%93%A5_Download_Aplicativo');
            return;
        }
        
        response.pipe(file);
        
        file.on('finish', function() {
            file.close();
            console.log('Download do APK concluído.');
        });
    }).on('error', function(err) {
        fs.unlink('build/suinocultura.apk');
        console.error('Erro ao baixar o APK:', err.message);
        // Cria um arquivo de texto como espaço reservado
        fs.writeFileSync('build/suinocultura.apk', 'Este é um arquivo de espaço reservado para o APK. O aplicativo real pode ser baixado em https://suinocultura.replit.app/pages/99_%F0%9F%93%A5_Download_Aplicativo');
    });
}

// Função para criar arquivo firebase-config.js com dados reais
function createFirebaseConfig() {
    console.log('Criando arquivo de configuração do Firebase...');
    
    const configContent = `// Configuração do Firebase
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Inicializar Firebase
firebase.initializeApp(firebaseConfig);
`;
    
    fs.writeFileSync('build/firebase-config.js', configContent);
    console.log('Arquivo firebase-config.js criado com sucesso.');
}

// Criar uma página de download simplificada
function createDownloadPage() {
    console.log('Criando página de download...');
    
    const downloadPageContent = `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Download - Sistema Suinocultura</title>
    <link rel="icon" href="favicon.ico">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #0B0B0F;
            color: #FAFAFA;
            line-height: 1.6;
            text-align: center;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .title {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #6BCB77, #4D96FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        .button {
            background: linear-gradient(45deg, #6BCB77, #4D96FF);
            color: white;
            border: none;
            padding: 0.8rem 2rem;
            font-size: 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.3s, box-shadow 0.3s;
            display: inline-block;
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(109, 203, 119, 0.15);
            margin: 2rem 0.5rem;
        }
        
        .button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(109, 203, 119, 0.25);
        }
        
        .card {
            background-color: #1C1C2A;
            border-radius: 12px;
            border: 1px solid #33334B;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 600px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Sistema Suinocultura</h1>
        <p>Download do Aplicativo Android</p>
        
        <div class="card">
            <h2>Aplicativo Android</h2>
            <p>Acesse o sistema completo diretamente do seu dispositivo Android, com todas as funcionalidades disponíveis mesmo em áreas com conexão limitada.</p>
            <a href="suinocultura.apk" class="button" download>Baixar APK</a>
            <a href="index.html" class="button">Voltar</a>
        </div>
        
        <div class="card">
            <h2>Instruções de Instalação</h2>
            <ol style="text-align: left;">
                <li>Baixe o arquivo APK</li>
                <li>No seu dispositivo Android, vá para Configurações > Segurança</li>
                <li>Ative a opção "Fontes desconhecidas" para permitir a instalação</li>
                <li>Abra o arquivo APK baixado para instalar</li>
                <li>Após a instalação, o aplicativo estará disponível no seu menu de aplicativos</li>
            </ol>
        </div>
    </div>
</body>
</html>`;
    
    fs.writeFileSync('build/download.html', downloadPageContent);
    console.log('Página de download criada com sucesso.');
}

// Executar script de build
async function buildProject() {
    console.log('Iniciando build do projeto para Firebase...');
    
    // Download do APK
    downloadAPK();
    
    // Criar arquivo de configuração do Firebase
    createFirebaseConfig();
    
    // Criar página de download
    createDownloadPage();
    
    console.log('Build concluído com sucesso!');
    console.log('Para fazer deploy no Firebase:');
    console.log('1. Atualize o arquivo firebase-config.js com suas credenciais reais');
    console.log('2. Execute: npx firebase login');
    console.log('3. Execute: npx firebase deploy');
}

// Executar build
buildProject();