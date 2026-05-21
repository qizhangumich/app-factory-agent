package com.appfactory.tipcalcdeluxe

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.appfactory.tipcalcdeluxe.model.CalculatorViewModel
import com.appfactory.tipcalcdeluxe.model.HistoryStore
import com.appfactory.tipcalcdeluxe.ui.MainCalculatorScreen
import com.appfactory.tipcalcdeluxe.ui.theme.TipCalculatorDeluxeTheme

/** Single-activity entry point hosting the Compose calculator UI. */
class MainActivity : ComponentActivity() {

    private val viewModel: CalculatorViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // SharedPreferences-backed history (spec.data_storage).
        val historyStore = HistoryStore(applicationContext)

        setContent {
            TipCalculatorDeluxeTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainCalculatorScreen(
                        viewModel = viewModel,
                        history = historyStore
                    )
                }
            }
        }
    }
}
