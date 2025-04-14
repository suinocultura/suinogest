package com.suinocultura.app;

import android.app.Application;
import timber.log.Timber;

/**
 * Classe de aplicativo para inicialização global
 */
public class SuinoculturaApp extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        
        // Inicializar Timber para logs (somente em debug)
        if (BuildConfig.DEBUG) {
            Timber.plant(new Timber.DebugTree());
        }
        
        // Inicializar configurações da aplicação
        initializeSettings();
    }
    
    /**
     * Inicializa as configurações padrão do aplicativo
     */
    private void initializeSettings() {
        // Configurações compartilhadas
        android.content.SharedPreferences prefs = getSharedPreferences("SuinoPrefs", MODE_PRIVATE);
        
        // Verificar primeira execução e definir valores padrão
        if (prefs.getBoolean("first_run", true)) {
            android.content.SharedPreferences.Editor editor = prefs.edit();
            
            // Definir valores padrão
            editor.putBoolean("first_run", false);
            editor.putBoolean("offline_mode_enabled", false);
            editor.putInt("cache_days", 7);
            editor.putString("default_view", "dashboard");
            
            editor.apply();
        }
    }
}