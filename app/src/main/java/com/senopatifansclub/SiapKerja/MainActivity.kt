package com.senopatifansclub.SiapKerja

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.senopatifansclub.SiapKerja.data.ServiceLocator
import com.senopatifansclub.SiapKerja.ui.theme.MyApplicationTheme
import com.senopatifansclub.SiapKerja.ui.SiapKerjaApp
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ServiceLocator.init(applicationContext)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                SiapKerjaApp()
            }
        }
    }
}
