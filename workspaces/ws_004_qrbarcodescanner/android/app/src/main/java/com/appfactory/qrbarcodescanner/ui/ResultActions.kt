package com.appfactory.qrbarcodescanner.ui

import android.content.ActivityNotFoundException
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.OpenInNew
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.appfactory.qrbarcodescanner.model.ScanContentType
import com.appfactory.qrbarcodescanner.model.ScanResult

/**
 * Reusable presentation of a [ScanResult]: type badge, content, optional
 * Wi-Fi details, and open / copy / share action buttons. Shared by the
 * scan result sheet and the history detail screen.
 */
@Composable
fun ResultActions(
    result: ScanResult,
    modifier: Modifier = Modifier,
) {
    val context = LocalContext.current
    var copied by remember { mutableStateOf(false) }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        // Type + symbology badge.
        Surface(
            color = MaterialTheme.colorScheme.primary,
            shape = RoundedCornerShape(50),
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Icon(
                    imageVector = result.contentType.icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimary,
                )
                Text(
                    text = "${result.contentType.displayName.uppercase()} · " +
                        result.symbology,
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            }
        }

        // Scrollable raw content.
        Surface(
            color = MaterialTheme.colorScheme.surfaceVariant,
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = result.value,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier
                    .padding(12.dp)
                    .heightIn(max = 180.dp)
                    .verticalScroll(rememberScrollState())
                    .semantics { contentDescription = "Scanned content" },
            )
        }

        // Wi-Fi specifics, when applicable.
        result.wifiCredentials?.let { wifi ->
            Column {
                Text(
                    "Network: ${wifi.ssid}",
                    style = MaterialTheme.typography.bodySmall,
                )
                if (wifi.password.isNotEmpty()) {
                    Text(
                        "Password: ${wifi.password}",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                Text(
                    "Security: ${wifi.security}",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        }

        // Action buttons.
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            openIntentFor(result)?.let { intent ->
                Button(
                    onClick = { safeStart(context, intent) },
                    modifier = Modifier.weight(1f),
                ) {
                    Icon(Icons.Filled.OpenInNew, contentDescription = null)
                    Text("  " + openLabel(result.contentType))
                }
            }

            OutlinedButton(
                onClick = {
                    copyToClipboard(context, result.value)
                    copied = true
                },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.outlinedButtonColors(),
            ) {
                Icon(
                    if (copied) Icons.Filled.Done else Icons.Filled.ContentCopy,
                    contentDescription = null,
                )
                Text(if (copied) "  Copied" else "  Copy")
            }

            OutlinedButton(
                onClick = { shareText(context, result.value) },
                modifier = Modifier.weight(1f),
            ) {
                Icon(Icons.Filled.Share, contentDescription = null)
                Text("  Share")
            }
        }
    }
}

/** Label for the "open" button, tailored to the content type. */
private fun openLabel(type: ScanContentType): String = when (type) {
    ScanContentType.URL -> "Open"
    ScanContentType.PHONE -> "Call"
    ScanContentType.EMAIL -> "Email"
    ScanContentType.SMS -> "Message"
    ScanContentType.GEO -> "Map"
    else -> "Open"
}

/** Builds an Intent for opening the result, or null if it is not openable. */
private fun openIntentFor(result: ScanResult): Intent? {
    val v = result.value.trim()
    return when (result.contentType) {
        ScanContentType.URL -> {
            val uri = if (v.startsWith("http", ignoreCase = true)) v else "https://$v"
            Intent(Intent.ACTION_VIEW, Uri.parse(uri))
        }
        ScanContentType.PHONE -> {
            val tel = if (v.startsWith("tel:", true)) v else "tel:$v"
            Intent(Intent.ACTION_DIAL, Uri.parse(tel))
        }
        ScanContentType.EMAIL -> {
            val addr = v.removePrefix("mailto:").removePrefix("MAILTO:")
            Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:$addr"))
        }
        ScanContentType.SMS -> Intent(Intent.ACTION_VIEW, Uri.parse(v))
        ScanContentType.GEO -> Intent(Intent.ACTION_VIEW, Uri.parse(v))
        else -> null
    }
}

private fun safeStart(context: Context, intent: Intent) {
    try {
        context.startActivity(intent)
    } catch (e: ActivityNotFoundException) {
        Toast.makeText(context, "No app can open this", Toast.LENGTH_SHORT).show()
    }
}

private fun copyToClipboard(context: Context, text: String) {
    val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    cm.setPrimaryClip(ClipData.newPlainText("Scan result", text))
    Toast.makeText(context, "Copied to clipboard", Toast.LENGTH_SHORT).show()
}

private fun shareText(context: Context, text: String) {
    val send = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    context.startActivity(Intent.createChooser(send, "Share scanned content"))
}
