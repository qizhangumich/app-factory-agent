package com.appfactory.qrbarcodescanner.scanner

import android.annotation.SuppressLint
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import com.appfactory.qrbarcodescanner.model.ScanResult
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage

/**
 * A CameraX [ImageAnalysis.Analyzer] that runs Google ML Kit's on-device
 * barcode scanner on every frame.
 *
 * The ML Kit model is bundled in the APK (see app/build.gradle.kts), so
 * detection is fully offline — no network access and no Play Services
 * model download.
 *
 * Repeated detections of the same value within [DEDUPE_MS] are suppressed
 * so a code lingering in frame does not flood the callback.
 */
class BarcodeAnalyzer(
    private val onScanned: (ScanResult) -> Unit,
) : ImageAnalysis.Analyzer {

    private val scanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                BarcodeSymbology.supportedFormats.first(),
                *BarcodeSymbology.supportedFormats.drop(1).toIntArray(),
            )
            .build()
    )

    private var lastValue: String? = null
    private var lastScanAt: Long = 0L

    @SuppressLint("UnsafeOptInUsageError")
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val input = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees,
        )

        scanner.process(input)
            .addOnSuccessListener { barcodes ->
                val barcode = barcodes.firstOrNull { !it.rawValue.isNullOrEmpty() }
                if (barcode != null) {
                    val value = barcode.rawValue!!
                    val now = System.currentTimeMillis()
                    val isDuplicate =
                        value == lastValue && (now - lastScanAt) < DEDUPE_MS
                    if (!isDuplicate) {
                        lastValue = value
                        lastScanAt = now
                        onScanned(
                            ScanResult(
                                value = value,
                                symbology = BarcodeSymbology.displayName(barcode.format),
                            )
                        )
                    }
                }
            }
            .addOnCompleteListener {
                // Always close the frame so CameraX can deliver the next one.
                imageProxy.close()
            }
    }

    /** Releases the ML Kit scanner. Call when the analyzer is no longer used. */
    fun close() {
        scanner.close()
    }

    companion object {
        private const val DEDUPE_MS = 2_000L
    }
}
