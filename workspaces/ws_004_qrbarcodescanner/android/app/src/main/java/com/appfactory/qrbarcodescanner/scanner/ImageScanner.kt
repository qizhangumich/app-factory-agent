package com.appfactory.qrbarcodescanner.scanner

import android.content.Context
import android.net.Uri
import com.appfactory.qrbarcodescanner.model.ScanResult
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

/**
 * Decodes a QR code or barcode from a static image (used by the
 * "scan from photo" import). Uses the same on-device ML Kit scanner.
 */
object ImageScanner {

    /**
     * Attempts to decode the first machine-readable code in the image at
     * [uri]. Returns null if no code is found or the image cannot be read.
     */
    suspend fun decode(context: Context, uri: Uri): ScanResult? =
        suspendCancellableCoroutine { cont ->
            val input = try {
                InputImage.fromFilePath(context, uri)
            } catch (e: Exception) {
                cont.resume(null)
                return@suspendCancellableCoroutine
            }

            val scanner = BarcodeScanning.getClient(
                BarcodeScannerOptions.Builder()
                    .setBarcodeFormats(
                        BarcodeSymbology.supportedFormats.first(),
                        *BarcodeSymbology.supportedFormats.drop(1).toIntArray(),
                    )
                    .build()
            )

            scanner.process(input)
                .addOnSuccessListener { barcodes ->
                    val barcode =
                        barcodes.firstOrNull { !it.rawValue.isNullOrEmpty() }
                    cont.resume(
                        barcode?.let {
                            ScanResult(
                                value = it.rawValue!!,
                                symbology = BarcodeSymbology.displayName(it.format),
                            )
                        }
                    )
                }
                .addOnFailureListener { cont.resume(null) }
                .addOnCompleteListener { scanner.close() }
        }
}
