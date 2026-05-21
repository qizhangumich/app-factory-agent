package com.appfactory.qrbarcodescanner

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.appfactory.qrbarcodescanner.ui.DetailScreen
import com.appfactory.qrbarcodescanner.ui.HistoryScreen
import com.appfactory.qrbarcodescanner.ui.QRScannerTheme
import com.appfactory.qrbarcodescanner.ui.ScannerScreen

/**
 * Single-activity entry point. Hosts the Compose UI and a lightweight,
 * state-driven navigation between the scanner, history, and detail screens.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            QRScannerTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppRoot()
                }
            }
        }
    }
}

/** The three top-level destinations. */
private sealed interface Screen {
    data object Scanner : Screen
    data object History : Screen
    data class Detail(val scanId: String) : Screen
}

/**
 * Root composable owning navigation state. State survives configuration
 * changes: the back stack of screen tags is saved, and detail re-resolves
 * its scan from the ViewModel by id.
 */
@Composable
private fun AppRoot() {
    val viewModel: ScannerViewModel = viewModel()

    // Current screen, with the detail's scan id persisted across rotation.
    var screenTag by rememberSaveable { mutableStateOf("scanner") }
    var detailId by rememberSaveable { mutableStateOf<String?>(null) }

    val screen: Screen = remember(screenTag, detailId) {
        when (screenTag) {
            "history" -> Screen.History
            "detail" -> detailId?.let { Screen.Detail(it) } ?: Screen.Scanner
            else -> Screen.Scanner
        }
    }

    when (screen) {
        Screen.Scanner -> ScannerScreen(
            viewModel = viewModel,
            onOpenHistory = { screenTag = "history" },
        )

        Screen.History -> HistoryScreen(
            viewModel = viewModel,
            onBack = { screenTag = "scanner" },
            onOpenDetail = { result ->
                detailId = result.id
                screenTag = "detail"
            },
        )

        is Screen.Detail -> {
            val result = viewModel.find(screen.scanId)
            if (result == null) {
                // Scan was deleted; fall back to the list.
                screenTag = "history"
            } else {
                DetailScreen(
                    result = result,
                    viewModel = viewModel,
                    onBack = { screenTag = "history" },
                )
            }
        }
    }
}
