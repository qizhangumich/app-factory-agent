package com.appfactory.qrbarcodescanner.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Message
import androidx.compose.material.icons.automirrored.filled.TextSnippet
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Link
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.ui.graphics.vector.ImageVector
import com.appfactory.qrbarcodescanner.model.ScanContentType

/** Material icon representing a [ScanContentType], for lists and badges. */
val ScanContentType.icon: ImageVector
    get() = when (this) {
        ScanContentType.URL -> Icons.Filled.Link
        ScanContentType.WIFI -> Icons.Filled.Wifi
        ScanContentType.CONTACT -> Icons.Filled.Person
        ScanContentType.PHONE -> Icons.Filled.Phone
        ScanContentType.EMAIL -> Icons.Filled.Email
        ScanContentType.SMS -> Icons.AutoMirrored.Filled.Message
        ScanContentType.GEO -> Icons.Filled.LocationOn
        ScanContentType.TEXT -> Icons.AutoMirrored.Filled.TextSnippet
    }
