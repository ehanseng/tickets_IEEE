"""
Script para agregar automáticamente la UI de gestión de modo de validación
a la página de tickets
"""

import re

def agregar_ui_validacion():
    print("=== Agregando UI de Validación a tickets.html ===\n")

    # Leer el archivo tickets.html
    with open('templates/tickets.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Leer el fragmento del modal
    with open('templates/validation_mode_modal_fragment.html', 'r', encoding='utf-8') as f:
        modal_content = f.read()

    modificaciones = []

    # 1. Agregar columna "Modo" en el encabezado
    print("1. Agregando columna 'Modo' en encabezado de tabla...")
    # Buscar después de la columna "Personas"
    header_pattern = r'(<th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Personas</th>)'
    header_replacement = r'\1\n                        <th class="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Modo</th>'

    if re.search(header_pattern, content):
        content = re.sub(header_pattern, header_replacement, content)
        modificaciones.append("[OK] Columna 'Modo' agregada al encabezado")
    else:
        print("   [AVISO] No se encontró el patrón del encabezado, puede que ya esté agregado")

    # 2. Agregar celda de modo en las filas
    print("2. Agregando celda de modo en las filas...")
    # Buscar el patrón de la celda de personas y código
    cell_pattern = r'(<td class="p-4">\{\{ ticket\.companions \+ 1 \}\}</td>)\s*(<td class="p-4 font-mono text-xs">)'

    cell_content = r'''\1
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
                        \2'''

    if re.search(cell_pattern, content):
        content = re.sub(cell_pattern, cell_content, content)
        modificaciones.append("[OK] Celda de modo agregada a las filas")
    else:
        print("   [AVISO] No se encontró el patrón de celdas")

    # 3. Agregar filtro de modo de validación
    print("3. Agregando filtro de modo de validación...")
    filter_pattern = r'(</select>\s*</div>\s*</div>)(\s*{% if tickets %})'

    filter_content = r'''<select id="validationModeFilter" onchange="filterTickets()" class="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                    <option value="all">Todos los modos</option>
                    <option value="once">Solo modo 'Once'</option>
                    <option value="daily">Solo modo 'Daily'</option>
                </select>
            </div>
        </div>\2'''

    if re.search(filter_pattern, content):
        content = re.sub(filter_pattern, filter_content, content)
        modificaciones.append("[OK] Filtro de modo de validacion agregado")
    else:
        print("   [AVISO] No se pudo agregar el filtro automáticamente")

    # 4. Agregar modal antes del cierre del script
    print("4. Agregando modal de gestión de validación...")
    # Buscar justo antes de </script>
    modal_pattern = r'(    \}\s*</script>)'

    if re.search(modal_pattern, content):
        # Extraer solo la parte del modal (sin el script que ya está dentro)
        modal_html = modal_content.split('<script>')[0]
        modal_js = modal_content.split('<script>')[1].split('</script>')[0]

        content = re.sub(
            modal_pattern,
            modal_html + '\n' + modal_js + '\n\\1',
            content
        )
        modificaciones.append("[OK] Modal de validacion agregado")
    else:
        print("   [AVISO] No se pudo insertar el modal automáticamente")

    # 5. Guardar el archivo modificado
    print("\n5. Guardando cambios...")
    with open('templates/tickets.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n=== Resumen de Modificaciones ===")
    for mod in modificaciones:
        print(f"  {mod}")

    print("\n[OK] Archivo tickets.html actualizado correctamente!")
    print("\nPara ver los cambios:")
    print("  1. Reinicia el servidor: uvicorn main:app --reload")
    print("  2. Abre: http://localhost:8000/admin/tickets")
    print("  3. Haz clic en 'Modo de Validacion'")

    return len(modificaciones) == 4


if __name__ == "__main__":
    try:
        success = agregar_ui_validacion()
        if success:
            print("\n[EXITO] Todo listo! La UI de validacion ha sido agregada exitosamente.")
        else:
            print("\n[AVISO] Algunos cambios no se pudieron aplicar automaticamente.")
            print("Consulta INSTRUCCIONES_UI_VALIDACION.md para hacerlo manualmente.")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("Consulta INSTRUCCIONES_UI_VALIDACION.md para hacerlo manualmente.")
