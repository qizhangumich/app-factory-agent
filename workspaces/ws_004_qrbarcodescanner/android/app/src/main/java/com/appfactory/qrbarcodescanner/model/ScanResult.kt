package com.appfactory.qrbarcodescanner.model

import org.json.JSONObject
import java.util.UUID

/**
 * Semantic classification of decoded content.
 */
enum class ScanContentType {
    URL, WIFI, CONTACT, PHONE, EMAIL, SMS, GEO, TEXT;

    /** Short, human-readable label for the type badge. */
    val displayName: String
        get() = when (this) {
            URL -> "Link"
            WIFI -> "Wi-Fi"
            CONTACT -> "Contact"
            PHONE -> "Phone"
            EMAIL -> "Email"
            SMS -> "SMS"
            GEO -> "Location"
            TEXT -> "Text"
        }
}

/** Parsed Wi-Fi credentials from a `WIFI:` payload. */
data class WiFiCredentials(
    val ssid: String,
    val password: String,
    val security: String,
    val hidden: Boolean,
)

/**
 * A single decoded code: raw value, symbology, detected content type and
 * capture time. Serialised to/from JSON for [HistoryStore] persistence.
 */
data class ScanResult(
    val id: String = UUID.randomUUID().toString(),
    val value: String,
    /** Barcode symbology, e.g. "QR Code", "EAN-13". */
    val symbology: String,
    val timestamp: Long = System.currentTimeMillis(),
) {
    /** Detected semantic content type. */
    val contentType: ScanContentType by lazy { detectType(value) }

    /** Single-line, trimmed preview suitable for list rows. */
    val preview: String
        get() {
            val collapsed = value.replace('\n', ' ').trim()
            return if (collapsed.length > 90) collapsed.take(90) + "…" else collapsed
        }

    /** Parsed Wi-Fi credentials when [contentType] is [ScanContentType.WIFI]. */
    val wifiCredentials: WiFiCredentials?
        get() = parseWiFi(value)

    /** Serialises this result to a JSON object. */
    fun toJson(): JSONObject = JSONObject().apply {
        put("id", id)
        put("value", value)
        put("symbology", symbology)
        put("timestamp", timestamp)
    }

    companion object {
        /** Reconstructs a [ScanResult] from a JSON object. */
        fun fromJson(json: JSONObject): ScanResult = ScanResult(
            id = json.optString("id", UUID.randomUUID().toString()),
            value = json.optString("value"),
            symbology = json.optString("symbology", "Barcode"),
            timestamp = json.optLong("timestamp", System.currentTimeMillis()),
        )

        /** Classifies a raw decoded string into a [ScanContentType]. */
        fun detectType(raw: String): ScanContentType {
            val trimmed = raw.trim()
            val lower = trimmed.lowercase()
            return when {
                lower.startsWith("wifi:") -> ScanContentType.WIFI
                lower.startsWith("begin:vcard") ||
                    lower.startsWith("mecard:") -> ScanContentType.CONTACT
                lower.startsWith("mailto:") -> ScanContentType.EMAIL
                lower.startsWith("tel:") -> ScanContentType.PHONE
                lower.startsWith("smsto:") ||
                    lower.startsWith("sms:") -> ScanContentType.SMS
                lower.startsWith("geo:") -> ScanContentType.GEO
                lower.startsWith("http://") ||
                    lower.startsWith("https://") -> ScanContentType.URL
                isLikelyBareUrl(trimmed) -> ScanContentType.URL
                isLikelyEmail(trimmed) -> ScanContentType.EMAIL
                else -> ScanContentType.TEXT
            }
        }

        /** True when the string looks like a bare URL without a scheme. */
        private fun isLikelyBareUrl(s: String): Boolean {
            if (s.contains(' ') || !s.contains('.')) return false
            val host = s.substringBefore('/')
            val parts = host.split('.')
            if (parts.size < 2) return false
            val tld = parts.last()
            return tld.length >= 2 && tld.all { it.isLetter() }
        }

        /** True when the string looks like a bare email address. */
        private fun isLikelyEmail(s: String): Boolean {
            if (s.contains(' ') || !s.contains('@') || !s.contains('.')) {
                return false
            }
            val parts = s.split('@')
            return parts.size == 2 && parts[1].contains('.')
        }

        /**
         * Parses a `WIFI:S:<ssid>;T:<type>;P:<password>;H:<hidden>;;` payload.
         * Handles `\;`, `\:` and `\\` escape sequences.
         */
        fun parseWiFi(raw: String): WiFiCredentials? {
            val trimmed = raw.trim()
            if (!trimmed.lowercase().startsWith("wifi:")) return null

            val body = trimmed.substring(5)
            val fields = mutableListOf<String>()
            val current = StringBuilder()
            var escaped = false
            for (ch in body) {
                when {
                    escaped -> { current.append(ch); escaped = false }
                    ch == '\\' -> escaped = true
                    ch == ';' -> { fields.add(current.toString()); current.clear() }
                    else -> current.append(ch)
                }
            }
            if (current.isNotEmpty()) fields.add(current.toString())

            var ssid = ""
            var password = ""
            var security = "nopass"
            var hidden = false
            for (field in fields) {
                val sep = field.indexOf(':')
                if (sep < 0) continue
                val key = field.substring(0, sep).uppercase()
                val v = field.substring(sep + 1)
                when (key) {
                    "S" -> ssid = v
                    "P" -> password = v
                    "T" -> security = v.ifEmpty { "nopass" }
                    "H" -> hidden = v.equals("true", ignoreCase = true)
                }
            }
            return if (ssid.isEmpty()) null
            else WiFiCredentials(ssid, password, security, hidden)
        }
    }
}
