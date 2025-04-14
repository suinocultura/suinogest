# Guia para Criação de APK do Sistema Suinocultura - Versão 2.1

Este guia detalhado explica como converter o Sistema de Gestão Suinocultura em um aplicativo Android (APK) utilizando a abordagem WebView. Esta abordagem permite empacotar a aplicação web Streamlit em um aplicativo Android nativo.

**Novidades na versão 2.1:**
- Suporte à integração com GitHub
- Visualização destacada de notas importantes
- Histórico de atualizações completo

## Pré-requisitos

1. **Android Studio** instalado em seu computador
   - Download: [https://developer.android.com/studio](https://developer.android.com/studio)
   
2. **JDK (Java Development Kit)** versão 8 ou superior
   - Download: [https://www.oracle.com/java/technologies/javase-downloads.html](https://www.oracle.com/java/technologies/javase-downloads.html)

3. **Sistema Suinocultura** hospedado em um servidor acessível via internet
   - O aplicativo irá carregar a versão hospedada do sistema

## Passos para Criação do APK

### 1. Configurar o Projeto Android

1. Abra o Android Studio
2. Selecione **File > New > Import Project**
3. Navegue até a pasta onde você extraiu os arquivos base do aplicativo Android fornecidos no pacote de download
4. Selecione a pasta `android_app_base` e clique em **OK**
5. Aguarde o Android Studio configurar o projeto

### 2. Configurar URL do Sistema

1. Abra o arquivo `MainActivity.java` localizado em:
   ```
   app/src/main/java/com/suinocultura/app/MainActivity.java
   ```

2. Localize a linha com a constante `STREAMLIT_URL`:
   ```java
   private static final String STREAMLIT_URL = "https://sistema-suinocultura.replit.app";
   ```

3. Substitua o URL pelo endereço onde seu sistema Suinocultura está hospedado (ou mantenha se estiver usando o Replit):
   ```java
   private static final String STREAMLIT_URL = "https://seu-servidor-real.com";
   ```

### 3. Personalizar o Ícone (Opcional)

1. Prepare seus ícones em diferentes tamanhos
2. No Android Studio, clique com o botão direito na pasta `res`
3. Selecione **New > Image Asset**
4. Siga o assistente para substituir os ícones padrão

### 4. Testar o Aplicativo

1. Conecte um dispositivo Android via USB ou configure um emulador
2. Clique no botão **Run** (triângulo verde) na barra de ferramentas
3. Selecione seu dispositivo/emulador e clique em **OK**
4. O aplicativo será instalado e executado no dispositivo

### 5. Gerar o APK de Versão de Lançamento

1. No menu, selecione **Build > Generate Signed Bundle / APK**
2. Selecione **APK** e clique em **Next**
3. Crie ou selecione uma keystore para assinar o APK:
   - Se for a primeira vez, clique em **Create new** e preencha os dados solicitados
   - Se já possui uma keystore, clique em **Choose existing** e selecione-a
4. Preencha as informações de keystore e clique em **Next**
5. Selecione a variante **release** e clique em **Finish**
6. Aguarde a conclusão da compilação

O APK será gerado na pasta:
```
app/release/app-release.apk
```

## Ajustes Adicionais Opcionais

### Personalizar as Cores do Aplicativo

1. Abra o arquivo `colors.xml` em `app/src/main/res/values/`
2. Modifique as cores para personalizar a aparência do aplicativo

### Configurar Cache Offline (Parcial)

1. Em `MainActivity.java`, você pode ajustar configurações adicionais do WebView para permitir cache:
   ```java
   webSettings.setAppCacheEnabled(true);
   webSettings.setCacheMode(WebSettings.LOAD_CACHE_ELSE_NETWORK);
   ```

### Otimizar para Tablets

1. Crie layouts alternativos para tablets em `res/layout-large/`
2. Ajuste as configurações de zoom no WebView conforme necessário

## Distribuição do APK

Após gerar o APK, você pode distribuí-lo das seguintes formas:

1. **Google Play Store** (recomendado para distribuição pública)
   - Requer conta de desenvolvedor Google Play ($25)
   - Processo de revisão pode levar alguns dias
   - [Console de Desenvolvedores Google Play](https://play.google.com/console/developers)

2. **Download Direto** 
   - Hospede o APK em seu servidor
   - Compartilhe o link direto para download
   - Os usuários precisarão habilitar "Fontes desconhecidas" nas configurações do Android

3. **Distribuição Interna**
   - Use serviços como Firebase App Distribution ou Google Play Internal Testing
   - Envie diretamente para dispositivos específicos

## Solução de Problemas

### O Aplicativo não Carrega o Sistema

- Verifique se o URL está correto e acessível
- Confirme se o sistema Streamlit está rodando no servidor
- Verifique permissões de internet no manifesto

### Erros de Compilação

- Atualize o Android Studio para a versão mais recente
- Sincronize o projeto com arquivos Gradle
- Verifique se todas as dependências estão instaladas

### Aplicativo Crasha ao Abrir

- Verifique os logs do Android Studio para identificar o erro
- Confirme se as permissões de internet estão declaradas no manifesto
- Teste em diferentes dispositivos/versões do Android

## Suporte Adicional

Para dúvidas ou problemas relacionados à configuração do APK, entre em contato com o suporte técnico do Sistema Suinocultura.