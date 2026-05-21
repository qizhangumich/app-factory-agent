package com.appfactory.unitconverterpro.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.StarBorder
import androidx.compose.material.icons.filled.SwapVert
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.appfactory.unitconverterpro.ConverterViewModel
import com.appfactory.unitconverterpro.R
import com.appfactory.unitconverterpro.model.ConvUnit
import com.appfactory.unitconverterpro.model.ConversionEngine
import com.appfactory.unitconverterpro.model.UnitCategory
import com.appfactory.unitconverterpro.model.UnitData
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Screen 2: two-field converter with live conversion, swap, favorite, copy,
 * and a related-conversions list.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConversionScreen(
    viewModel: ConverterViewModel,
    categoryId: String,
    initialFromId: String,
    initialToId: String,
    initialValue: String,
    onBack: () -> Unit
) {
    val category = remember(categoryId) {
        UnitData.category(categoryId) ?: UnitData.categories.first()
    }
    val favorites by viewModel.favorites.collectAsState()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    var fromUnit by remember(categoryId) {
        mutableStateOf(category.unit(initialFromId) ?: category.units[0])
    }
    var toUnit by remember(categoryId) {
        mutableStateOf(
            category.unit(initialToId)
                ?: category.units.getOrElse(1) { category.units[0] }
        )
    }
    var inputText by remember(categoryId) { mutableStateOf(initialValue) }

    val parsedInput = ConversionEngine.parse(inputText)
    val resultValue = parsedInput?.let {
        ConversionEngine.convert(it, fromUnit, toUnit, category)
    }
    val isFavorite = favorites.any {
        it.categoryId == category.id &&
            it.fromUnitId == fromUnit.id &&
            it.toUnitId == toUnit.id
    }

    // Debounced history recording: log once the user pauses typing.
    LaunchedEffect(inputText, fromUnit, toUnit) {
        delay(900)
        val input = ConversionEngine.parse(inputText) ?: return@LaunchedEffect
        val result = ConversionEngine.convert(input, fromUnit, toUnit, category)
            ?: return@LaunchedEffect
        viewModel.addHistory(category.id, fromUnit.id, toUnit.id, input, result)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(category.nameRes)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.action_back)
                        )
                    }
                },
                actions = {
                    IconButton(onClick = {
                        viewModel.toggleFavorite(category.id, fromUnit.id, toUnit.id)
                    }) {
                        Icon(
                            imageVector = if (isFavorite) Icons.Filled.Star
                            else Icons.Filled.StarBorder,
                            contentDescription = stringResource(
                                if (isFavorite) R.string.a11y_unfavorite
                                else R.string.a11y_favorite
                            ),
                            tint = if (isFavorite) Color(0xFFFFC107)
                            else MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Converter card
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                shape = RoundedCornerShape(20.dp)
            ) {
                Column(Modifier.padding(16.dp)) {
                    UnitFieldRow(
                        roleLabel = stringResource(R.string.label_from),
                        category = category,
                        selectedUnit = fromUnit,
                        onUnitSelected = { fromUnit = it },
                        value = inputText,
                        onValueChange = { inputText = sanitize(it) },
                        editable = true
                    )

                    // Swap button
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(40.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = MaterialTheme.colorScheme.tertiary,
                            modifier = Modifier.size(40.dp)
                        ) {
                            IconButton(onClick = {
                                val oldFrom = fromUnit
                                fromUnit = toUnit
                                toUnit = oldFrom
                                resultValue?.let {
                                    inputText = ConversionEngine.plainString(it)
                                }
                            }) {
                                Icon(
                                    Icons.Filled.SwapVert,
                                    contentDescription = stringResource(R.string.a11y_swap),
                                    tint = Color.White
                                )
                            }
                        }
                    }

                    UnitFieldRow(
                        roleLabel = stringResource(R.string.label_to),
                        category = category,
                        selectedUnit = toUnit,
                        onUnitSelected = { toUnit = it },
                        value = resultValue?.let { ConversionEngine.format(it) } ?: "",
                        onValueChange = {},
                        editable = false
                    )
                }
            }

            // Action row
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(
                    onClick = {
                        resultValue?.let {
                            copyToClipboard(context, ConversionEngine.format(it))
                            scope.launch {
                                snackbarHostState.showSnackbar(
                                    context.getString(R.string.toast_copied)
                                )
                            }
                        }
                    },
                    enabled = resultValue != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Filled.ContentCopy, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text(stringResource(R.string.action_copy))
                }
                FilledTonalButton(
                    onClick = {
                        viewModel.toggleFavorite(category.id, fromUnit.id, toUnit.id)
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        if (isFavorite) Icons.Filled.Star else Icons.Filled.StarBorder,
                        contentDescription = null
                    )
                    Spacer(Modifier.width(8.dp))
                    Text(
                        stringResource(
                            if (isFavorite) R.string.action_unfavorite
                            else R.string.action_favorite
                        )
                    )
                }
            }

            // Related conversions
            Text(
                text = stringResource(R.string.section_related),
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            val related = category.units.filter {
                it.id != toUnit.id && it.id != fromUnit.id
            }.take(5)
            related.forEach { unit ->
                val converted = parsedInput?.let {
                    ConversionEngine.convert(it, fromUnit, unit, category)
                }
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    ),
                    shape = RoundedCornerShape(12.dp),
                    onClick = { toUnit = unit }
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 14.dp, vertical = 12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("${stringResource(unit.nameRes)} (${unit.symbol})")
                        Text(
                            converted?.let { ConversionEngine.format(it) } ?: "—",
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

/** One labeled row of the converter: a value field plus a unit dropdown. */
@Composable
private fun UnitFieldRow(
    roleLabel: String,
    category: UnitCategory,
    selectedUnit: ConvUnit,
    onUnitSelected: (ConvUnit) -> Unit,
    value: String,
    onValueChange: (String) -> Unit,
    editable: Boolean
) {
    var menuExpanded by remember { mutableStateOf(false) }

    Column(Modifier.padding(vertical = 8.dp)) {
        Text(
            roleLabel,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(4.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (editable) {
                OutlinedTextField(
                    value = value,
                    onValueChange = onValueChange,
                    modifier = Modifier.weight(1f),
                    textStyle = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
            } else {
                Text(
                    text = value.ifEmpty { "—" },
                    fontSize = 22.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(Modifier.width(12.dp))
            Box {
                FilledTonalButton(onClick = { menuExpanded = true }) {
                    Text(selectedUnit.symbol)
                }
                DropdownMenu(
                    expanded = menuExpanded,
                    onDismissRequest = { menuExpanded = false }
                ) {
                    category.units.forEach { unit ->
                        DropdownMenuItem(
                            text = {
                                Text("${stringResource(unit.nameRes)} (${unit.symbol})")
                            },
                            onClick = {
                                onUnitSelected(unit)
                                menuExpanded = false
                            }
                        )
                    }
                }
            }
        }
    }
}

/** Restricts input to characters that can form a number. */
private fun sanitize(raw: String): String {
    val allowed = "0123456789.,-eE ".toSet()
    return raw.filter { it in allowed }
}

private fun copyToClipboard(context: Context, text: String) {
    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    clipboard.setPrimaryClip(ClipData.newPlainText("conversion_result", text))
}
