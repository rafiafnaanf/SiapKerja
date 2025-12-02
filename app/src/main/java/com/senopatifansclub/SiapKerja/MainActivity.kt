package com.senopatifansclub.SiapKerja

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.senopatifansclub.SiapKerja.data.ServiceLocator
import com.senopatifansclub.SiapKerja.ui.theme.MyApplicationTheme
import com.senopatifansclub.SiapKerja.ui.SiapKerjaApp
import com.senopatifansclub.SiapKerja.ui.settings.SettingsViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ServiceLocator.init(applicationContext)
        enableEdgeToEdge()
        setContent {
            val settingsViewModel: SettingsViewModel = viewModel()
            val settingsState by settingsViewModel.uiState.collectAsState()
            MyApplicationTheme(themeMode = settingsState.themeMode) { SiapKerjaApp() }
        }
    }
}
