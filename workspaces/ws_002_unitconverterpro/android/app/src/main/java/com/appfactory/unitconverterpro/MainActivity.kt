package com.appfactory.unitconverterpro

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.CompareArrows
import androidx.compose.material.icons.filled.History
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.appfactory.unitconverterpro.ui.ConversionScreen
import com.appfactory.unitconverterpro.ui.CategoryListScreen
import com.appfactory.unitconverterpro.ui.HistoryScreen
import com.appfactory.unitconverterpro.ui.theme.UnitConverterProTheme

class MainActivity : ComponentActivity() {

    private val viewModel: ConverterViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            UnitConverterProTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AppRoot(viewModel)
                }
            }
        }
    }
}

/** Routes for the navigation graph. */
private object Routes {
    const val CATEGORIES = "categories"
    const val HISTORY = "history"
    // Conversion takes a category id plus optional from/to/value query params.
    const val CONVERSION = "conversion/{categoryId}?from={from}&to={to}&value={value}"

    fun conversion(
        categoryId: String,
        from: String? = null,
        to: String? = null,
        value: String? = null
    ): String {
        val f = from ?: ""
        val t = to ?: ""
        val v = value ?: "1"
        return "conversion/$categoryId?from=$f&to=$t&value=$v"
    }
}

@Composable
private fun AppRoot(viewModel: ConverterViewModel) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.hierarchy?.firstOrNull()?.route

    Scaffold(
        bottomBar = {
            // Hide the bottom bar on the conversion detail screen.
            val showBar = currentRoute == Routes.CATEGORIES || currentRoute == Routes.HISTORY
            if (showBar) {
                NavigationBar {
                    NavigationBarItem(
                        selected = currentRoute == Routes.CATEGORIES,
                        onClick = {
                            navController.navigate(Routes.CATEGORIES) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = {
                            Icon(
                                Icons.AutoMirrored.Filled.CompareArrows,
                                contentDescription = null
                            )
                        },
                        label = { Text(stringResource(R.string.tab_convert)) }
                    )
                    NavigationBarItem(
                        selected = currentRoute == Routes.HISTORY,
                        onClick = {
                            navController.navigate(Routes.HISTORY) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(Icons.Filled.History, contentDescription = null) },
                        label = { Text(stringResource(R.string.tab_history)) }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = Routes.CATEGORIES,
            modifier = Modifier.padding(padding)
        ) {
            composable(Routes.CATEGORIES) {
                CategoryListScreen(
                    viewModel = viewModel,
                    onOpenCategory = { categoryId, from, to ->
                        navController.navigate(Routes.conversion(categoryId, from, to))
                    }
                )
            }
            composable(Routes.HISTORY) {
                HistoryScreen(
                    viewModel = viewModel,
                    onReopen = { categoryId, from, to, value ->
                        navController.navigate(
                            Routes.conversion(categoryId, from, to, value)
                        )
                    }
                )
            }
            composable(Routes.CONVERSION) { entry ->
                val args = entry.arguments
                ConversionScreen(
                    viewModel = viewModel,
                    categoryId = args?.getString("categoryId").orEmpty(),
                    initialFromId = args?.getString("from").orEmpty(),
                    initialToId = args?.getString("to").orEmpty(),
                    initialValue = args?.getString("value") ?: "1",
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
