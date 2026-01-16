// Top-level build file where you can add configuration options common to all sub-projects/modules.
// Project: sms
plugins {
    id("com.android.application") version "8.3.0" apply false
    id("com.android.library") version "8.3.0" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    // Required for Firebase
    id("com.google.gms.google-services") version "4.4.2" apply false
    // Required for Compose in Kotlin 2.0+
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
    alias(libs.plugins.google.android.libraries.mapsplatform.secrets.gradle.plugin) apply false
}
tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}