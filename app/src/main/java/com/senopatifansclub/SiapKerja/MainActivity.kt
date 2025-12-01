package com.senopatifansclub.SiapKerja

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.senopatifansclub.SiapKerja.ui.theme.MyApplicationTheme
import kotlinx.coroutines.delay

// --- MOCK BACKEND & DATABASE (Singleton) ---
object MockRepository {
    var isLoggedIn by mutableStateOf(false)
    var currentUser: User? = null

    // Simulasi Database User
    data class User(
        val name: String,
        val email: String,
        val careerInterest: String,
        val skillLevel: String = "Junior"
    )

    // Simulasi Data AI Response untuk CV
    val cvAnalysisResult = """
        Posisi: Backend Engineer
        Rating: 8.5/10
        
        Kelebihan:
        - Pengalaman Python kuat
        - Pemahaman Database baik
        
        Kekurangan:
        - Kurang pengalaman di Cloud (AWS/GCP)
        
        Rekomendasi Career Pathway:
        1. Pelajari Docker & Kubernetes
        2. Ambil sertifikasi AWS Basic
    """.trimIndent()

    // Simulasi Pertanyaan Interview berdasarkan Level
    fun getInterviewQuestion(level: String): String {
        return when(level) {
            "Entry Level" -> "Ceritakan tentang diri Anda dan mengapa Anda tertarik memulai karir di bidang ini?"
            "Mid Level" -> "Jelaskan tantangan teknis terbesar yang pernah Anda hadapi dan bagaimana Anda menyelesaikannya?"
            "Senior" -> "Bagaimana Anda merancang arsitektur sistem yang scalable untuk menangani 1 juta request per detik?"
            else -> "Pertanyaan default."
        }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                SiapKerjaApp()
            }
        }
    }
}

@Composable
fun SiapKerjaApp() {
    // Cek status login dari MockRepository
    if (MockRepository.isLoggedIn) {
        MainScreen()
    } else {
        AuthScreen()
    }
}

// --- AUTH SCREEN (Login/Register) ---
@Composable
fun AuthScreen() {
    var isRegister by remember { mutableStateOf(false) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var interest by remember { mutableStateOf("") }

    val context = LocalContext.current

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = if (isRegister) "Daftar SiapKerja" else "Masuk SiapKerja",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(32.dp))

            if (isRegister) {
                OutlinedTextField(
                    value = name, onValueChange = { name = it },
                    label = { Text("Nama Lengkap") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = interest, onValueChange = { interest = it },
                    label = { Text("Minat Karir (cth: Backend)") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
            }

            OutlinedTextField(
                value = email, onValueChange = { email = it },
                label = { Text("Email") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(
                value = password, onValueChange = { password = it },
                label = { Text("Password") },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = {
                    if (email.isNotEmpty() && password.isNotEmpty()) {
                        // Simulasi Login/Register Berhasil
                        MockRepository.currentUser = MockRepository.User(
                            name = if (name.isNotEmpty()) name else "User Demo",
                            email = email,
                            careerInterest = if (interest.isNotEmpty()) interest else "Software Engineer"
                        )
                        MockRepository.isLoggedIn = true
                        Toast.makeText(context, "Selamat Datang!", Toast.LENGTH_SHORT).show()
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (isRegister) "Daftar" else "Masuk")
            }

            TextButton(onClick = { isRegister = !isRegister }) {
                Text(if (isRegister) "Sudah punya akun? Masuk" else "Belum punya akun? Daftar")
            }
        }
    }
}

// --- MAIN SCREEN (Navigation Suite) ---
@Composable
fun MainScreen() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.REVIEW_CV) }

    NavigationSuiteScaffold(
        navigationSuiteItems = {
            AppDestinations.entries.forEach {
                item(
                    icon = { Icon(it.icon, contentDescription = it.label) },
                    label = { Text(it.label) },
                    selected = it == currentDestination,
                    onClick = { currentDestination = it }
                )
            }
        }
    ) {
        Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                when (currentDestination) {
                    AppDestinations.REVIEW_CV -> ReviewCVScreen()
                    AppDestinations.INTERVIEW -> InterviewScreen()
                    AppDestinations.PROFILE -> ProfileScreen()
                }
            }
        }
    }
}

enum class AppDestinations(val label: String, val icon: ImageVector) {
    REVIEW_CV("Review CV", Icons.Default.Description),
    INTERVIEW("Interview", Icons.Default.VideoCameraFront),
    PROFILE("Profil", Icons.Default.AccountCircle),
}

// --- FEATURE 1: REVIEW CV SCREEN ---
@Composable
fun ReviewCVScreen() {
    var isUploading by remember { mutableStateOf(false) }
    var showResult by remember { mutableStateOf(false) }

    // Simulasi proses upload
    LaunchedEffect(isUploading) {
        if (isUploading) {
            delay(2000) // Simulasi loading 2 detik
            isUploading = false
            showResult = true
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Review CV & Career Pathway", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(24.dp))

        if (!showResult && !isUploading) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(
                    modifier = Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(Icons.Default.UploadFile, contentDescription = null, modifier = Modifier.size(48.dp))
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Upload CV Anda (PDF)")
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { isUploading = true }) {
                        Text("Pilih File")
                    }
                }
            }
        } else if (isUploading) {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text("Sedang menganalisis CV dengan AI...")
        } else {
            // Hasil Analisis
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Hasil Analisis AI", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                    Text(MockRepository.cvAnalysisResult)
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = { showResult = false }) {
                Text("Upload CV Baru")
            }
        }
    }
}

// --- FEATURE 2: INTERVIEW SCREEN ---
@Composable
fun InterviewScreen() {
    var step by remember { mutableStateOf(0) } // 0: Setup, 1: Interview, 2: Result
    var difficulty by remember { mutableStateOf("Entry Level") }
    var currentQuestion by remember { mutableStateOf("") }
    var userAnswer by remember { mutableStateOf("") }
    var aiFeedback by remember { mutableStateOf("") }

    // Simulasi Sensor
    var isCameraActive by remember { mutableStateOf(false) }
    var distanceStatus by remember { mutableStateOf("Mendeteksi...") }

    // Simulasi Proximity Logic (Mock)
    LaunchedEffect(isCameraActive) {
        if (isCameraActive) {
            while(true) {
                delay(1000)
                distanceStatus = listOf("Jarak Pas", "Terlalu Dekat", "Jarak Pas").random()
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text("Simulasi Interview AI", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(16.dp))

        when (step) {
            0 -> { // Setup Difficulty
                Text("Pilih Tingkat Kesulitan:")
                listOf("Entry Level", "Mid Level", "Senior").forEach { level ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        RadioButton(selected = (difficulty == level), onClick = { difficulty = level })
                        Text(level)
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = {
                        currentQuestion = MockRepository.getInterviewQuestion(difficulty)
                        isCameraActive = true
                        step = 1
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Mulai Interview")
                }
            }
            1 -> { // Interview Process
                // Simulasi Kamera View
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(250.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color.Black)
                        .border(2.dp, if(distanceStatus == "Jarak Pas") Color.Green else Color.Red, RoundedCornerShape(12.dp)),
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Default.Face, contentDescription = null, tint = Color.White, modifier = Modifier.size(64.dp))
                        Text("Kamera Aktif (Simulasi)", color = Color.White)
                        Text("Status: $distanceStatus", color = if(distanceStatus == "Jarak Pas") Color.Green else Color.Red, fontWeight = FontWeight.Bold)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Pertanyaan AI
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Pertanyaan AI:", fontWeight = FontWeight.Bold)
                        Text(currentQuestion)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Input Jawaban (Simulasi STT)
                OutlinedTextField(
                    value = userAnswer,
                    onValueChange = { userAnswer = it },
                    label = { Text("Jawaban Anda") },
                    modifier = Modifier.fillMaxWidth().height(120.dp),
                    trailingIcon = {
                        IconButton(onClick = {
                            // Simulasi STT: Mengisi teks otomatis
                            userAnswer = "Saya memiliki pengalaman dalam menangani masalah ini dengan menggunakan pendekatan sistematis, memecah masalah menjadi bagian kecil, dan menyelesaikannya satu per satu."
                        }) {
                            Icon(Icons.Default.Mic, contentDescription = "Bicara", tint = MaterialTheme.colorScheme.primary)
                        }
                    }
                )
                Text("Tekan ikon mikrofon untuk simulasi bicara (TTS)", style = MaterialTheme.typography.bodySmall, color = Color.Gray)

                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = {
                        isCameraActive = false
                        aiFeedback = "Jawaban Anda cukup baik secara struktur. Namun, cobalah untuk lebih spesifik memberikan contoh kasus nyata (metode STAR). Kepercayaan diri terlihat baik dari kamera."
                        step = 2
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = userAnswer.isNotEmpty()
                ) {
                    Text("Kirim Jawaban")
                }
            }
            2 -> { // Result
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Feedback AI", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                        HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                        Text(aiFeedback)
                    }
                }
                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = {
                        userAnswer = ""
                        step = 0
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Kembali ke Menu Utama")
                }
            }
        }
    }
}

// --- FEATURE 3: PROFILE SCREEN ---
@Composable
fun ProfileScreen() {
    val user = MockRepository.currentUser

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = Icons.Default.AccountCircle,
            contentDescription = null,
            modifier = Modifier.size(100.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(16.dp))

        Text(user?.name ?: "Guest", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Text(user?.email ?: "-", style = MaterialTheme.typography.bodyMedium, color = Color.Gray)

        Spacer(modifier = Modifier.height(32.dp))

        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Informasi Karir", fontWeight = FontWeight.Bold)
                HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Minat:")
                    Text(user?.careerInterest ?: "-")
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Level Saat Ini:")
                    Text(user?.skillLevel ?: "-")
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = { MockRepository.isLoggedIn = false },
            colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Keluar (Logout)")
        }
    }
}