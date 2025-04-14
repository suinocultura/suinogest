package com.suinocultura.app;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import android.annotation.SuppressLint;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Toast;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.content.Context;
import android.webkit.JavascriptInterface;

/**
 * MainActivity do aplicativo Suinocultura
 * Versão 2.1 (2025)
 * Esta classe gerencia a interface principal do aplicativo, que carrega a aplicação Streamlit via WebView
 * Atualização 2.1: Suporte à visualização de atualizações do sistema e integração com GitHub
 */
public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private ProgressBar progressBar;
    private LinearLayout offlineLayout;
    private Button retryButton;
    private SharedPreferences preferences;
    
    // URL da sua aplicação Streamlit hospedada
    private static final String STREAMLIT_URL = "https://workspace.ruanlouco231.repl.co";
    
    // Nome do arquivo de preferências
    private static final String PREFS_NAME = "SuinoPrefs";
    private static final String PREF_LAST_UPDATE = "lastUpdate";
    
    // Página de erro offline (HTML mais elaborado)
    private static final String OFFLINE_HTML = "<html><body style='text-align:center; padding:20px; font-family: Arial, sans-serif;'>" +
            "<div style='max-width:500px; margin:0 auto; padding:20px; border-radius:8px; background-color:#f8f9fa;'>" +
            "<h2 style='color:#dc3545;'>Sem conexão com a Internet</h2>" +
            "<div style='width:80px; height:80px; margin:20px auto; background-color:#f8d7da; border-radius:50%; display:flex; justify-content:center; align-items:center;'>" +
            "<span style='font-size:40px;'>📶</span></div>" +
            "<p style='color:#333; font-size:16px;'>O Sistema de Gestão Suinocultura precisa de conexão com a Internet para funcionar.</p>" +
            "<p style='color:#555; font-size:14px; margin-bottom:25px;'>Por favor, verifique sua conexão e tente novamente.</p>" +
            "<p style='font-size:12px; margin-top:30px; color:#777;'>Data da última atualização: <span id='lastUpdate'>Desconhecida</span></p>" +
            "<button onclick='window.location.reload();' style='background-color:#007bff; color:white; border:none; border-radius:4px; padding:12px 24px; font-size:16px; cursor:pointer; margin-top:10px;'>Tentar novamente</button>" +
            "</div>" +
            "<script>" +
            "document.getElementById('lastUpdate').innerText = AndroidInterface.getLastUpdateDate();" +
            "</script>" +
            "</body></html>";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Inicializar componentes
        webView = findViewById(R.id.webView);
        swipeRefreshLayout = findViewById(R.id.swipeRefresh);
        progressBar = findViewById(R.id.progressBar);
        offlineLayout = findViewById(R.id.offlineLayout);
        retryButton = findViewById(R.id.retryButton);
        
        // Carregar preferências
        preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        
        // Configurar WebView
        setupWebView();
        
        // Configurar SwipeRefreshLayout
        swipeRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                reloadWebView();
            }
        });
        
        // Configurar botão de nova tentativa
        retryButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                reloadWebView();
            }
        });
        
        // Verificar conexão e carregar conteúdo apropriado
        if (isNetworkAvailable()) {
            loadStreamlitApp();
            updateLastSync();
        } else {
            showOfflineView();
        }
    }
    
    private void updateLastSync() {
        // Atualizar data da última sincronização
        SharedPreferences.Editor editor = preferences.edit();
        editor.putLong(PREF_LAST_UPDATE, System.currentTimeMillis());
        editor.apply();
    }
    
    private String getLastUpdateDate() {
        long lastUpdate = preferences.getLong(PREF_LAST_UPDATE, 0);
        if (lastUpdate == 0) {
            return "Nunca sincronizado";
        }
        
        // Formatar data
        java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("dd/MM/yyyy HH:mm");
        return sdf.format(new java.util.Date(lastUpdate));
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                // Interceptar URLs e decidir como lidar com elas
                return false;  // false permite o WebView processar o URL
            }
            
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
                
                // Mostrar WebView e esconder layout offline
                webView.setVisibility(View.VISIBLE);
                offlineLayout.setVisibility(View.GONE);
            }
            
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                
                // Verificar se é a página principal que falhou
                if (request.isForMainFrame()) {
                    showOfflineView();
                }
            }
        });
        
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        
        // Configurações para melhor desempenho
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setAppCacheEnabled(true);
        webSettings.setAppCachePath(getApplicationContext().getCacheDir().getAbsolutePath());
        webSettings.setDatabaseEnabled(true);
        webSettings.setGeolocationEnabled(true);
        
        // Interface JavaScript para comunicação entre WebView e código nativo
        webView.addJavascriptInterface(new WebAppInterface(), "AndroidInterface");
    }
    
    /**
     * Interface JavaScript para permitir que o código HTML acesse funções nativas
     */
    private class WebAppInterface {
        @JavascriptInterface
        public String getLastUpdateDate() {
            return MainActivity.this.getLastUpdateDate();
        }
    }

    private void loadStreamlitApp() {
        // Mostrar tela de carregamento
        progressBar.setVisibility(View.VISIBLE);
        webView.setVisibility(View.VISIBLE);
        offlineLayout.setVisibility(View.GONE);
        
        // Carregar URL da aplicação Streamlit
        webView.loadUrl(STREAMLIT_URL);
    }
    
    private void showOfflineMessage() {
        webView.loadDataWithBaseURL(null, OFFLINE_HTML, "text/html", "UTF-8", null);
    }
    
    private void showOfflineView() {
        // Esconder WebView e mostrar layout offline
        webView.setVisibility(View.GONE);
        offlineLayout.setVisibility(View.VISIBLE);
        swipeRefreshLayout.setRefreshing(false);
        progressBar.setVisibility(View.GONE);
    }
    
    private void reloadWebView() {
        if (isNetworkAvailable()) {
            loadStreamlitApp();
        } else {
            showOfflineView();
            Toast.makeText(this, R.string.error_connection, Toast.LENGTH_SHORT).show();
        }
        
        // Esconder indicador de atualização após 1 segundo
        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                swipeRefreshLayout.setRefreshing(false);
            }
        }, 1000);
    }
    
    private boolean isNetworkAvailable() {
        ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
        return activeNetworkInfo != null && activeNetworkInfo.isConnected();
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            // Perguntar se o usuário deseja sair
            new AlertDialog.Builder(this)
                    .setTitle("Sair do aplicativo")
                    .setMessage("Deseja realmente sair do Sistema Suinocultura?")
                    .setPositiveButton("Sim", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            MainActivity.super.onBackPressed();
                        }
                    })
                    .setNegativeButton("Não", null)
                    .show();
        }
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main_menu, true);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        
        if (id == R.id.action_refresh) {
            reloadWebView();
            return true;
        } else if (id == R.id.action_about) {
            showAboutDialog();
            return true;
        } else if (id == R.id.action_updates) {
            loadUpdatesPage();
            return true;
        } else if (id == R.id.action_exit) {
            confirmExit();
            return true;
        }
        
        return super.onOptionsItemSelected(item);
    }
    
    /**
     * Carrega a página de histórico de atualizações do sistema
     */
    private void loadUpdatesPage() {
        if (isNetworkAvailable()) {
            // Navegar para a página do Sistema Desenvolvedor - Aba de Atualizações
            webView.loadUrl(STREAMLIT_URL + "?page=98_%F0%9F%9B%A0%EF%B8%8F_Sistema_Desenvolvedor#Atualizacoes");
            Toast.makeText(this, R.string.updates_title, Toast.LENGTH_SHORT).show();
        } else {
            showOfflineView();
            Toast.makeText(this, R.string.error_connection, Toast.LENGTH_SHORT).show();
        }
    }
    
    /**
     * Confirma saída do aplicativo
     */
    private void confirmExit() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.exit_title)
                .setMessage(R.string.exit_message)
                .setPositiveButton(R.string.yes, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        MainActivity.super.onBackPressed();
                    }
                })
                .setNegativeButton(R.string.no, null)
                .show();
    }
    
    private void showAboutDialog() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.about_title)
                .setMessage("Sistema de Gestão Suinocultura\n" +
                        "Versão 2.1 (2025)\n\n" +
                        "Este aplicativo oferece acesso ao sistema completo de gestão para suinocultura, " +
                        "incluindo controle de animais, ciclos reprodutivos, alimentação, saúde e relatórios.\n\n" +
                        "Novidades na versão 2.1:\n" +
                        "• Suporte à integração com GitHub\n" +
                        "• Visualização destacada de notas importantes\n" +
                        "• Histórico de atualizações completo\n\n" +
                        "Última atualização: " + getLastUpdateDate())
                .setPositiveButton(R.string.ok, null)
                .show();
    }
}