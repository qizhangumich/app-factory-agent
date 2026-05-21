package com.appfactory.qrbarcodescanner.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.FlashlightOff
import androidx.compose.material.icons.filled.FlashlightOn
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.NoPhotography
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.appfactory.qrbarcodescanner.ScannerViewModel
import com.appfactory.qrbarcodescanner.scanner.ImageScanner
import kotlinx.coroutines.launch

/**
 * Primary screen: full-screen CameraX preview, scan-target overlay,
 * flashlight (top-right), history (top-left), photo import (bottom-left),
 * and a result bottom sheet on detection.
 */
@Composable
fun ScannerScreen(
    viewModel: ScannerViewModel,
    onOpenHistory: () -> Unit,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val currentResult by viewModel.currentResult.collectAsStateValue()
    val torchOn by viewModel.torchOn.collectAsStateValue()
    val importError by viewModel.importError.collectAsStateValue()

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED
        )
    }
    var permissionRequested by remember { mutableStateOf(false) }
    var flashGreen by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        permissionRequested = true
    }

    val photoLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        if (uri != null) {
            scope.launch {
                val result = ImageScanner.decode(context, uri)
                if (result != null) {
                    viewModel.onScanned(result)
                } else {
                    viewModel.reportImportFailure(
                        "No QR code or barcode found in that image."
                    )
                }
            }
        }
    }

    // Request camera permission once on first appearance.
    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    // Briefly flash the reticle green when a new result arrives.
    LaunchedEffect(currentResult?.id) {
        if (currentResult != null) {
            flashGreen = true
            kotlinx.coroutines.delay(350)
            flashGreen = false
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (hasCameraPermission) {
            CameraPreview(
                torchEnabled = torchOn,
                analysisPaused = currentResult != null,
                onScanned = { result ->
                    if (currentResult == null) {
                        Haptics.success(context)
                        viewModel.onScanned(result)
                    }
                },
                modifier = Modifier.fillMaxSize(),
            )
            ScanOverlay(flashSuccess = flashGreen)
            ScannerControls(
                torchOn = torchOn,
                onToggleTorch = {
                    Haptics.tick(context)
                    viewModel.toggleTorch()
                },
                onOpenHistory = onOpenHistory,
                onImportPhoto = { photoLauncher.launch("image/*") },
            )
        } else {
            PermissionDeniedContent(
                permissionRequested = permissionRequested,
                onRequest = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                onOpenSettings = {
                    context.startActivity(
                        Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                            data = Uri.fromParts("package", context.packageName, null)
                        }
                    )
                },
                onImportPhoto = { photoLauncher.launch("image/*") },
            )
        }

        // Result bottom sheet.
        currentResult?.let { result ->
            ResultSheet(result = result, onDismiss = { viewModel.dismissResult() })
        }
    }

    // Photo-import failure dialog.
    importError?.let { message ->
        AlertDialog(
            onDismissRequest = { viewModel.clearImportError() },
            confirmButton = {
                TextButton(onClick = { viewModel.clearImportError() }) {
                    Text("OK")
                }
            },
            title = { Text("No Code Found") },
            text = { Text(message) },
        )
    }
}

/** Overlaid camera controls: history, flashlight, hint, photo import. */
@Composable
private fun ScannerControls(
    torchOn: Boolean,
    onToggleTorch: () -> Unit,
    onOpenHistory: () -> Unit,
    onImportPhoto: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            CircleControl(
                icon = Icons.Filled.History,
                description = "Scan history",
                onClick = onOpenHistory,
            )
            CircleControl(
                icon = if (torchOn) Icons.Filled.FlashlightOn
                else Icons.Filled.FlashlightOff,
                description = if (torchOn) "Turn flashlight off"
                else "Turn flashlight on",
                tint = if (torchOn) Color(0xFFFFD60A) else Color.White,
                onClick = onToggleTorch,
            )
        }

        Spacer(modifier = Modifier.weight(1f))

        Surface(
            color = Color.Black.copy(alpha = 0.45f),
            shape = RoundedCornerShape(50),
            modifier = Modifier.align(Alignment.CenterHorizontally),
        ) {
            Text(
                "Point the camera at a QR code or barcode",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
            )
        }

        Spacer(modifier = Modifier.size(14.dp))

        Row(modifier = Modifier.fillMaxWidth()) {
            CircleControl(
                icon = Icons.Filled.Image,
                description = "Scan a code from a photo",
                onClick = onImportPhoto,
            )
        }
    }
}

/** A circular translucent control button used over the camera. */
@Composable
private fun CircleControl(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    description: String,
    tint: Color = Color.White,
    onClick: () -> Unit,
) {
    IconButton(
        onClick = onClick,
        modifier = Modifier
            .size(48.dp)
            .semantics { contentDescription = description },
        colors = IconButtonDefaults.iconButtonColors(
            containerColor = Color.Black.copy(alpha = 0.5f),
            contentColor = tint,
        ),
    ) {
        Icon(imageVector = icon, contentDescription = null)
    }
}

/** Shown when camera permission is missing. */
@Composable
private fun PermissionDeniedContent(
    permissionRequested: Boolean,
    onRequest: () -> Unit,
    onOpenSettings: () -> Unit,
    onImportPhoto: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            Icons.Filled.NoPhotography,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.size(16.dp))
        Text(
            "Camera Access Needed",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold,
        )
        Spacer(modifier = Modifier.size(8.dp))
        Text(
            "QR & Barcode Scanner+ needs the camera to scan codes. " +
                "Grant camera access to start scanning.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Spacer(modifier = Modifier.size(20.dp))
        // After a denial the system dialog won't reappear; send to Settings.
        Button(onClick = if (permissionRequested) onOpenSettings else onRequest) {
            Text(if (permissionRequested) "Open Settings" else "Grant Camera Access")
        }
        Spacer(modifier = Modifier.size(8.dp))
        OutlinedButton(onClick = onImportPhoto) {
            Text("Scan from a Photo")
        }
    }
}
