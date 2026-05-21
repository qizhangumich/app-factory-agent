package com.appfactory.unitconverterpro.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.appfactory.unitconverterpro.ConverterViewModel
import com.appfactory.unitconverterpro.R
import com.appfactory.unitconverterpro.model.UnitCategory
import com.appfactory.unitconverterpro.model.UnitData

/**
 * Screen 1: searchable category grid with a pinned favorites row.
 *
 * @param onOpenCategory invoked with (categoryId, fromUnitId?, toUnitId?)
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CategoryListScreen(
    viewModel: ConverterViewModel,
    onOpenCategory: (String, String?, String?) -> Unit
) {
    val favorites by viewModel.favorites.collectAsState()
    var query by remember { mutableStateOf("") }

    Scaffold(
        topBar = { TopAppBar(title = { Text(stringResource(R.string.app_name)) }) }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding)) {

            // Search field
            TextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text(stringResource(R.string.search_prompt)) },
                leadingIcon = { Icon(Icons.Filled.Search, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(14.dp),
                colors = TextFieldDefaults.colors(
                    focusedIndicatorColor = androidx.compose.ui.graphics.Color.Transparent,
                    unfocusedIndicatorColor = androidx.compose.ui.graphics.Color.Transparent
                )
            )

            val context = androidx.compose.ui.platform.LocalContext.current
            // Resolve localized category names for searching.
            val matchedCategories = remember(query) {
                if (query.isBlank()) {
                    UnitData.categories
                } else {
                    val q = query.lowercase()
                    UnitData.categories.filter {
                        context.getString(it.nameRes).lowercase().contains(q)
                    }
                }
            }

            LazyVerticalGrid(
                columns = GridCells.Adaptive(minSize = 160.dp),
                contentPadding = PaddingValues(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                if (favorites.isNotEmpty() && query.isBlank()) {
                    item(span = { GridItemSpan(maxLineSpan) }) {
                        FavoritesRow(favorites, onOpenCategory)
                    }
                }
                item(span = { GridItemSpan(maxLineSpan) }) {
                    Text(
                        text = stringResource(R.string.section_categories),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                items(matchedCategories, key = { it.id }) { category ->
                    CategoryCard(category) { onOpenCategory(category.id, null, null) }
                }
            }
        }
    }
}

@Composable
private fun FavoritesRow(
    favorites: List<com.appfactory.unitconverterpro.model.FavoritePair>,
    onOpenCategory: (String, String?, String?) -> Unit
) {
    Column {
        Text(
            text = stringResource(R.string.section_favorites),
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(8.dp))
        LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            items(favorites, key = { it.id }) { fav ->
                val category = UnitData.category(fav.categoryId)
                val from = category?.unit(fav.fromUnitId)
                val to = category?.unit(fav.toUnitId)
                if (category != null && from != null && to != null) {
                    Card(
                        modifier = Modifier
                            .width(140.dp)
                            .clip(RoundedCornerShape(14.dp)),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surface
                        ),
                        onClick = { onOpenCategory(category.id, from.id, to.id) }
                    ) {
                        Column(Modifier.padding(12.dp)) {
                            Icon(
                                category.icon,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(Modifier.height(6.dp))
                            Text(
                                "${from.symbol} → ${to.symbol}",
                                fontWeight = FontWeight.SemiBold,
                                style = MaterialTheme.typography.bodyMedium
                            )
                            Text(
                                stringResource(category.nameRes),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        }
        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun CategoryCard(category: UnitCategory, onClick: () -> Unit) {
    val subtitle = category.units.take(2).joinToString(" · ") { it.symbol }
    val name = stringResource(category.nameRes)
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(124.dp)
            .semantics { contentDescription = name },
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        onClick = onClick
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(
                category.icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(30.dp)
            )
            Text(name, style = MaterialTheme.typography.titleMedium)
            Text(
                subtitle,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
