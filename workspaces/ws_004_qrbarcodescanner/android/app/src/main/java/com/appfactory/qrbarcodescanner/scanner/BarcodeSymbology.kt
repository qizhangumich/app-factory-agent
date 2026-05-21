package com.appfactory.qrbarcodescanner.scanner

import com.google.mlkit.vision.barcode.common.Barcode

/**
 * Maps ML Kit barcode format constants to the symbology names declared in
 * the app spec, and provides the set of formats the scanner detects.
 */
object BarcodeSymbology {

    /**
     * Every barcode format the scanner listens for. Covers QR plus all 1D/2D
     * barcodes in the spec: EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39,
     * ITF, PDF417, Aztec, Data Matrix.
     */
    val supportedFormats = intArrayOf(
        Barcode.FORMAT_QR_CODE,
        Barcode.FORMAT_EAN_13,
        Barcode.FORMAT_EAN_8,
        Barcode.FORMAT_UPC_A,
        Barcode.FORMAT_UPC_E,
        Barcode.FORMAT_CODE_128,
        Barcode.FORMAT_CODE_39,
        Barcode.FORMAT_CODE_93,
        Barcode.FORMAT_ITF,
        Barcode.FORMAT_PDF417,
        Barcode.FORMAT_AZTEC,
        Barcode.FORMAT_DATA_MATRIX,
    )

    /** Human-readable name for an ML Kit barcode format constant. */
    fun displayName(format: Int): String = when (format) {
        Barcode.FORMAT_QR_CODE -> "QR Code"
        Barcode.FORMAT_EAN_13 -> "EAN-13"
        Barcode.FORMAT_EAN_8 -> "EAN-8"
        Barcode.FORMAT_UPC_A -> "UPC-A"
        Barcode.FORMAT_UPC_E -> "UPC-E"
        Barcode.FORMAT_CODE_128 -> "Code 128"
        Barcode.FORMAT_CODE_39 -> "Code 39"
        Barcode.FORMAT_CODE_93 -> "Code 93"
        Barcode.FORMAT_ITF -> "ITF"
        Barcode.FORMAT_PDF417 -> "PDF417"
        Barcode.FORMAT_AZTEC -> "Aztec"
        Barcode.FORMAT_DATA_MATRIX -> "Data Matrix"
        else -> "Barcode"
    }
}
