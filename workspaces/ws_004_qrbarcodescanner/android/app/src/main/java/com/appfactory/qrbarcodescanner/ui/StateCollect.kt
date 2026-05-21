package com.appfactory.qrbarcodescanner.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.runtime.collectAsState
import kotlinx.coroutines.flow.StateFlow

/**
 * Thin alias over [collectAsState] for [StateFlow], used throughout the UI
 * for brevity. Equivalent to `flow.collectAsState()`.
 */
@Composable
fun <T> StateFlow<T>.collectAsStateValue(): State<T> = collectAsState()
