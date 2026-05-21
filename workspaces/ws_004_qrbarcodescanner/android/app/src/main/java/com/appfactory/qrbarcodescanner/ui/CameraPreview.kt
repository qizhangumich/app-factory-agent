package com.appfactory.qrbarcodescanner.ui

import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import com.appfactory.qrbarcodescanner.model.ScanResult
import com.appfactory.qrbarcodescanner.scanner.BarcodeAnalyzer
import java.util.concurrent.Executors

/**
 * CameraX preview bound into Compose via [AndroidView].
 *
 * Builds a [Preview] + [ImageAnalysis] use-case pair, attaches a
 * [BarcodeAnalyzer] (ML Kit) to the analysis stream, and binds them to the
 * back camera for the composition's lifecycle. The torch is driven by
 * [torchEnabled]; [analysisPaused] stops emitting results while the result
 * sheet is open.
 */
@Composable
fun CameraPreview(
    torchEnabled: Boolean,
    analysisPaused: Boolean,
    onScanned: (ScanResult) -> Unit,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val previewView = remember {
        PreviewView(context).apply {
            scaleType = PreviewView.ScaleType.FILL_CENTER
        }
    }
    val analysisExecutor = remember { Executors.newSingleThreadExecutor() }
    val cameraControl = remember { mutableStateOf<androidx.camera.core.CameraControl?>(null) }
    // Held so the analyzer can be released on dispose.
    val analyzerRef = remember { mutableStateOf<BarcodeAnalyzer?>(null) }
    // Latest callback, read indirectly so rebinding is not needed each frame.
    val pausedState = remember { mutableStateOf(analysisPaused) }
    pausedState.value = analysisPaused

    LaunchedEffect(Unit) {
        val cameraProvider = ProcessCameraProvider.getInstance(context).get()

        val preview = Preview.Builder().build().also {
            it.setSurfaceProvider(previewView.surfaceProvider)
        }

        val analyzer = BarcodeAnalyzer { result ->
            // Drop frames while the result sheet is showing.
            if (!pausedState.value) onScanned(result)
        }
        analyzerRef.value = analyzer

        val imageAnalysis = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { it.setAnalyzer(analysisExecutor, analyzer) }

        try {
            cameraProvider.unbindAll()
            val camera = cameraProvider.bindToLifecycle(
                lifecycleOwner,
                CameraSelector.DEFAULT_BACK_CAMERA,
                preview,
                imageAnalysis,
            )
            cameraControl.value = camera.cameraControl
            camera.cameraControl.enableTorch(torchEnabled)
        } catch (e: Exception) {
            // Camera unavailable (e.g. emulator without camera). Preview
            // simply stays blank; the permission/empty UI handles messaging.
        }
    }

    // React to torch toggles without rebinding the whole camera.
    LaunchedEffect(torchEnabled) {
        cameraControl.value?.enableTorch(torchEnabled)
    }

    DisposableEffect(Unit) {
        onDispose {
            analyzerRef.value?.close()
            analysisExecutor.shutdown()
        }
    }

    AndroidView(factory = { previewView }, modifier = modifier)
}
