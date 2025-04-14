# Sistema Suinocultura Offline

Aplicativo para gerenciamento de suinocultura offline, desenvolvido com Kivy e SQLite.

## Sobre o Aplicativo

Este aplicativo foi desenvolvido para fornecer uma versão offline do Sistema Suinocultura, permitindo que os usuários:

- Acessem e gerenciem dados mesmo sem conexão com a internet
- Cadastrem e monitorem animais
- Registrem eventos de saúde, reprodução e crescimento
- Exportem e importem dados para sincronização com o sistema online

## Instalação

Para instalar o aplicativo em um dispositivo Android:

1. Baixe o arquivo APK do aplicativo no seu dispositivo Android
2. Permita a instalação de aplicativos de fontes desconhecidas nas configurações do seu dispositivo
3. Abra o arquivo APK e siga as instruções para instalar

## Compilação

Para compilar o aplicativo a partir do código fonte:

1. Certifique-se de ter o Python, Kivy e Buildozer instalados
2. Clone este repositório
3. Execute o comando:

```bash
buildozer -v android debug
```

4. O APK será gerado na pasta bin/

## Primeiro Acesso

Ao acessar o aplicativo pela primeira vez, use as seguintes credenciais:

- **Matrícula**: 123456
- **Nome**: Administrador
- **Cargo**: Admin

## Sincronização de Dados

### Exportação Manual
Para exportar dados manualmente:

1. No menu principal, selecione "Exportar Dados"
2. Os dados serão exportados para a pasta "dados_exportados" no armazenamento do dispositivo
3. O arquivo exportado terá o formato "suinocultura_export_YYYYMMDD_HHMMSS.json"

### Importação Manual
Para importar dados manualmente:

1. Coloque o arquivo JSON na pasta "dados_exportados" no armazenamento do dispositivo
2. Reinicie o aplicativo
3. No menu principal, selecione "Importar Dados"

### Sincronização com Firebase Firestore
Para sincronizar automaticamente com o Firestore:

1. No menu principal, selecione "Sincronizar com Cloud"
2. Se o dispositivo estiver online, os dados serão enviados para o Firestore
3. Os dados são isolados por usuário para garantir a segurança
4. A sincronização ocorre nos dois sentidos quando disponível

### Configuração da API de Sincronização
Para configurar a API de sincronização:

1. No aplicativo móvel, a URL da API está definida em `main.py`
2. No Streamlit Cloud, configure as credenciais do Firebase nas secrets
3. A API utiliza tokens de autenticação para garantir segurança

## Recursos

O aplicativo possui os seguintes módulos principais:

- **Cadastro de Animais**: registro e gerenciamento de todos os animais
- **Reprodução**: acompanhamento de ciclos reprodutivos (em desenvolvimento)
- **Crescimento**: monitoramento de peso e desenvolvimento (em desenvolvimento)
- **Saúde**: registro de eventos de saúde, vacinações e tratamentos (em desenvolvimento)
- **Relatórios**: visualização de dados estatísticos (em desenvolvimento)

## Requisitos de Sistema

- Android 5.0 (API 21) ou superior
- Armazenamento mínimo: 50 MB
- RAM mínima: 1 GB

## Contato e Suporte

Para suporte técnico ou dúvidas sobre o aplicativo, entre em contato através do sistema online ou pelo e-mail de suporte disponibilizado pela administração.

---

© 2025 Sistema Suinocultura - Todos os direitos reservados