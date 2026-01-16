package com.example.sms

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.provider.Telephony
import android.text.method.HideReturnsTransformationMethod
import android.text.method.PasswordTransformationMethod
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.database.FirebaseDatabase

class MainActivity : AppCompatActivity() {

    private lateinit var auth: FirebaseAuth
    private lateinit var statusBadge: TextView
    private lateinit var authSection: LinearLayout
    private lateinit var exportSection: LinearLayout
    private lateinit var loadingBar: ProgressBar

    override fun onCreate(savedInstanceState: Bundle?) {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        auth = FirebaseAuth.getInstance()

        statusBadge = findViewById(R.id.statusBadge)
        authSection = findViewById(R.id.authSection)
        exportSection = findViewById(R.id.exportSection)
        loadingBar = findViewById(R.id.loadingBar)

        val emailInput = findViewById<EditText>(R.id.emailInput)
        val passwordInput = findViewById<EditText>(R.id.passwordInput)

        // --- ADDED: PASSWORD VISIBILITY LOGIC ---
        val showPasswordCheckbox = findViewById<CheckBox>(R.id.showPassword)
        showPasswordCheckbox.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                passwordInput.transformationMethod = HideReturnsTransformationMethod.getInstance()
            } else {
                passwordInput.transformationMethod = PasswordTransformationMethod.getInstance()
            }
            passwordInput.setSelection(passwordInput.text.length)
        }

        findViewById<Button>(R.id.btnLogin).setOnClickListener {
            val email = emailInput.text.toString().trim()
            val pass = passwordInput.text.toString().trim()
            if (email.isNotEmpty() && pass.isNotEmpty()) {
                setLoading(true)
                auth.signInWithEmailAndPassword(email, pass).addOnCompleteListener { task ->
                    setLoading(false)
                    if (task.isSuccessful) updateUI()
                    else Toast.makeText(this, "Login Failed: ${task.exception?.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }

        findViewById<TextView>(R.id.btnSignup).setOnClickListener {
            val email = emailInput.text.toString().trim()
            val pass = passwordInput.text.toString().trim()
            if (email.isNotEmpty() && pass.isNotEmpty()) {
                setLoading(true)
                auth.createUserWithEmailAndPassword(email, pass).addOnCompleteListener { task ->
                    if (task.isSuccessful) {
                        auth.currentUser?.sendEmailVerification()
                        Toast.makeText(this, "Verification email sent!", Toast.LENGTH_LONG).show()
                    }
                    setLoading(false)
                    updateUI()
                }
            }
        }

        findViewById<Button>(R.id.btnExport).setOnClickListener {
            setLoading(true)
            auth.currentUser?.reload()?.addOnCompleteListener {
                setLoading(false)
                if (auth.currentUser?.isEmailVerified == true) {
                    checkSmsPermission()
                } else {
                    Toast.makeText(this, "Please verify your email first!", Toast.LENGTH_SHORT).show()
                }
            }
        }

        findViewById<TextView>(R.id.btnSignout).setOnClickListener {
            auth.signOut()
            updateUI()
        }

        updateUI()
    }

    private fun setLoading(isLoading: Boolean) {
        loadingBar.visibility = if (isLoading) View.VISIBLE else View.GONE
    }

    private fun updateUI() {
        val user = auth.currentUser
        if (user == null) {
            authSection.visibility = View.VISIBLE
            exportSection.visibility = View.GONE
            statusBadge.text = "NOT LOGGED IN"
            statusBadge.setTextColor(Color.parseColor("#64748B"))
        } else {
            authSection.visibility = View.GONE
            exportSection.visibility = View.VISIBLE
            if (user.isEmailVerified) {
                statusBadge.text = "VERIFIED ✅"
                statusBadge.setTextColor(Color.parseColor("#059669"))
            } else {
                statusBadge.text = "PENDING VERIFICATION ⏳"
                statusBadge.setTextColor(Color.parseColor("#2563EB"))
            }
        }
    }

    private fun checkSmsPermission() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.READ_SMS), 100)
        } else {
            syncData()
        }
    }

    // --- UPDATED: REAL SMS EXTRACTION LOGIC ---
    private fun syncData() {
        val user = auth.currentUser ?: return
        val smsList = mutableListOf<Map<String, String>>()

        val cursor = contentResolver.query(
            Telephony.Sms.CONTENT_URI,
            arrayOf(Telephony.Sms.ADDRESS, Telephony.Sms.BODY),
            null, null, null
        )

        cursor?.use {
            val addressIndex = it.getColumnIndex(Telephony.Sms.ADDRESS)
            val bodyIndex = it.getColumnIndex(Telephony.Sms.BODY)

            while (it.moveToNext()) {
                val sender = it.getString(addressIndex) ?: "Unknown"
                val message = it.getString(bodyIndex) ?: ""
                smsList.add(mapOf("sender" to sender, "message" to message))
            }
        }

        if (smsList.isNotEmpty()) {
            setLoading(true)
            val db = FirebaseDatabase.getInstance().reference.child("user_sms").child(user.uid)
            db.setValue(smsList).addOnSuccessListener {
                setLoading(false)
                Toast.makeText(this, "Exported ${smsList.size} messages!", Toast.LENGTH_LONG).show()
            }.addOnFailureListener { e ->
                setLoading(false)
                Toast.makeText(this, "Export Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        } else {
            Toast.makeText(this, "No messages found to export", Toast.LENGTH_SHORT).show()
        }
    }
}