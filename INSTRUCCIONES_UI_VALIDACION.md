# Instrucciones para Agregar UI de Validación al Frontend

## ✅ Ya está hecho

1. **API Backend**: Todos los endpoints ya están creados y funcionando
2. **Modal HTML**: El modal completo está en `templates/validation_mode_modal_fragment.html`
3. **Botón**: Ya agregué el botón "Modo de Validación" en la barra superior

## 📝 Pasos para completar la integración

### Paso 1: Agregar el Modal al archivo tickets.html

Abre el archivo [`templates/tickets.html`](templates/tickets.html) y **ANTES de la línea que dice `</div>` (la última del archivo, justo antes de `{% endblock %}`)**:

**Busca esta sección (cerca de la línea 1941):**
```html
    }
</script>
{% endblock %}
```

**Inserta TODO el contenido del archivo** [`templates/validation_mode_modal_fragment.html`](templates/validation_mode_modal_fragment.html) **ANTES del `</script>`**

### Paso 2: Agregar columna de Modo de Validación en la tabla

En el mismo archivo `templates/tickets.html`:

**A. Busca la sección de encabezados de tabla (alrededor de la línea 97):**
```html
<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Personas</th>
<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Código</th>
```

**Agregar DESPUÉS de "Personas" y ANTES de "Código":**
```html
<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Modo</th>
```

**B. Busca donde se crean las filas de la tabla (alrededor de línea 124-145):**
Busca esta estructura:
```html
<td class="p-4">{{ ticket.companions + 1 }}</td>
<td class="p-4 font-mono text-xs">...</td>
```

**Agregar ENTRE esas dos líneas:**
```html
<td class="p-4">
    {% if ticket.validation_mode == 'daily' %}
    <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium bg-green-100 text-green-700 border border-green-200">
        <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
        </svg>
        Diario
    </span>
    {% else %}
    <span class="inline-flex items-center rounded-full px-2 py-1 text-xs font-medium bg-orange-100 text-orange-700 border border-orange-200">
        <svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        Una vez
    </span>
    {% endif %}
</td>
```

### Paso 3: Agregar filtro por modo de validación

En la sección de filtros (alrededor de línea 52-64), **agregar después del filtro de eventos**:

```html
<select id="validationModeFilter" onchange="filterTickets()" class="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
    <option value="all">Todos los modos</option>
    <option value="once">Solo modo 'Once'</option>
    <option value="daily">Solo modo 'Daily'</option>
</select>
```

### Paso 4: Actualizar la función filterTickets()

Busca la función `filterTickets()` en el JavaScript (alrededor de línea 1800) y **agregar este filtro** dentro de la función:

```javascript
// Filtrar por modo de validación
const validationModeFilter = document.getElementById('validationModeFilter')?.value || 'all';
if (validationModeFilter !== 'all') {
    const modeCell = row.cells[4]; // Ajustar índice según posición de la columna
    const isDaily = modeCell?.textContent.includes('Diario');
    const isOnce = modeCell?.textContent.includes('Una vez');

    if (validationModeFilter === 'daily' && !isDaily) return;
    if (validationModeFilter === 'once' && !isOnce) return;
}
```

### Paso 5: Agregar checkboxes para selección múltiple

**A. En el encabezado de la tabla, agregar como PRIMERA columna:**
```html
<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground w-12">
    <input type="checkbox" id="selectAll" onchange="toggleSelectAll()" class="rounded border-gray-300">
</th>
```

**B. En cada fila de la tabla, agregar como PRIMERA celda:**
```html
<td class="p-4">
    <input type="checkbox" name="ticketSelect" value="{{ ticket.id }}" onchange="updateSelectedCount()" class="rounded border-gray-300">
</td>
```

**C. Agregar esta función JavaScript:**
```javascript
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll').checked;
    document.querySelectorAll('input[name="ticketSelect"]').forEach(cb => {
        cb.checked = selectAll;
    });
    if (typeof updateSelectedCount === 'function') {
        updateSelectedCount();
    }
}
```

## 🎨 Resultado Final

Cuando termines, tendrás:

1. ✅ **Botón "Modo de Validación"** en la barra superior (ya agregado)
2. ✅ **Modal completo** con dos métodos:
   - Cambiar por evento completo (con estadísticas en tiempo real)
   - Cambiar tickets seleccionados (con checkboxes)
3. ✅ **Columna "Modo"** en la tabla mostrando:
   - 🟢 Badge verde "Diario" para modo daily
   - 🟠 Badge naranja "Una vez" para modo once
4. ✅ **Filtro** para ver solo tickets de un modo específico
5. ✅ **Checkboxes** para selección múltiple
6. ✅ **Estadísticas** en tiempo real del evento seleccionado

## 🧪 Cómo Probar

1. Abre la página de tickets: `http://localhost:8000/admin/tickets`
2. Haz clic en "Modo de Validación"
3. Selecciona un evento
4. Ve las estadísticas actualizarse automáticamente
5. Elige el modo (once o daily)
6. Haz clic en "Aplicar Cambios"
7. La página se recargará mostrando los cambios

## 💡 Alternativa Rápida: Script Automático

Si prefieres, puedo crear un script Python que haga todos estos cambios automáticamente en el archivo HTML. ¿Te gustaría que lo haga?

## 📸 Vista Previa del Modal

El modal mostrará:
- **Dos métodos de selección**: Por evento o tickets individuales
- **Estadísticas en tiempo real**: Total, modo once, modo daily, validados
- **Dos modos de validación**: Visual con iconos y descripciones
- **Confirmación**: Muestra cuántos tickets se actualizarán
- **Feedback**: Mensaje de éxito y recarga automática

¿Necesitas ayuda con algún paso específico?
