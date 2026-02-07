# Sistema de Tags/Etiquetas para Usuarios

## Descripción

El sistema de tags permite categorizar usuarios con múltiples etiquetas. Esto es útil para identificar a qué organización o grupo pertenece cada usuario. Un usuario puede tener múltiples tags simultáneamente.

## Características Principales

- ✅ **Tags múltiples por usuario**: Un usuario puede tener varios tags (ej: "IEEE Tadeo" + "IEEE YP Co")
- ✅ **Detección de duplicados inteligente**: Al importar usuarios, si ya existen (por email), se les agrega el nuevo tag sin eliminar los existentes
- ✅ **Colores personalizables**: Cada tag tiene un color hex para mejor visualización
- ✅ **Visualización en interfaz**: Los tags se muestran como badges de colores en la lista de usuarios
- ✅ **API REST completa**: Endpoints para gestionar tags y asignarlos a usuarios

## Estructura de Base de Datos

### Tabla `tags`
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL UNIQUE,
    color VARCHAR DEFAULT '#3B82F6',
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabla `user_tags` (Many-to-Many)
```sql
CREATE TABLE user_tags (
    user_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tag_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
)
```

## Tags Predeterminados

1. **IEEE Tadeo** (Azul: #3B82F6)
   - Usuarios de IEEE Tadeo Student Branch
   - Asignado a todos los usuarios existentes

2. **IEEE YP Co** (Verde: #10B981)
   - Usuarios de IEEE Young Professionals Colombia
   - Disponible para nuevas importaciones

## API Endpoints

### Listar Tags
```http
GET /tags/
Query params:
  - active_only: bool = True
  - skip: int = 0
  - limit: int = 200
```

### Crear Tag (Solo ADMIN)
```http
POST /tags/
Body: {
  "name": "IEEE WIE",
  "color": "#EC4899",
  "description": "IEEE Women in Engineering"
}
```

### Obtener Tag
```http
GET /tags/{tag_id}
```

### Actualizar Tag (Solo ADMIN)
```http
PUT /tags/{tag_id}
Body: {
  "name": "Nuevo Nombre",
  "color": "#10B981",
  "description": "Nueva descripción",
  "is_active": true
}
```

### Eliminar Tag (Solo ADMIN)
```http
DELETE /tags/{tag_id}
```
**Nota**: No se puede eliminar si hay usuarios asociados

### Agregar Tag a Usuario (Solo ADMIN)
```http
POST /users/{user_id}/tags/{tag_id}
```

### Remover Tag de Usuario (Solo ADMIN)
```http
DELETE /users/{user_id}/tags/{tag_id}
```

## Importación de Usuarios con Tags

### Script: `import_users_with_tags.py`

Este script permite importar usuarios desde un archivo CSV y asignarles un tag automáticamente. Si el usuario ya existe (por email), se le agrega el nuevo tag sin eliminar los existentes.

### Uso
```bash
python import_users_with_tags.py <archivo.csv> <nombre_tag>
```

### Ejemplo
```bash
python import_users_with_tags.py usuarios_yp.csv "IEEE YP Co"
```

### Formato CSV
```csv
name,email,phone,country_code,identification,university_name,is_ieee_member,ieee_member_id
María García,maria@ieee.org,3001234567,+57,1234567890,Universidad Nacional,true,12345678
```

### Campos CSV
- **name**: Nombre completo (requerido)
- **email**: Correo electrónico (requerido, usado para detectar duplicados)
- **phone**: Número de teléfono (opcional)
- **country_code**: Código de país con + (default: +57)
- **identification**: Cédula o documento (opcional)
- **university_name**: Nombre exacto de la universidad (opcional)
- **is_ieee_member**: true/false (default: false)
- **ieee_member_id**: ID de membresía IEEE (opcional)

### Comportamiento de Importación

#### Usuario Nuevo
- Se crea el usuario con todos los datos del CSV
- Se le asigna el tag especificado
- Mensaje: `✓ Usuario CREADO con tag 'IEEE YP Co'`

#### Usuario Duplicado (email existente)
- **NO se modifica** la información del usuario existente
- Se le **agrega** el nuevo tag (preservando los existentes)
- Mensaje: `⟳ Ya existe - Tag 'IEEE YP Co' AGREGADO`

#### Usuario con Tag Existente
- No se hace ningún cambio
- Mensaje: `⟳ Ya existe y ya tiene el tag 'IEEE YP Co'`

### Ejemplo de Importación

**Primera importación** (usuarios existentes de IEEE Tadeo):
```
Erick Hansen (erick@elaborando.co)
  Tags: [IEEE Tadeo]
```

**Después de importar con tag "IEEE YP Co"**:
```
Erick Hansen (erick@elaborando.co)
  Tags: [IEEE Tadeo, IEEE YP Co]  ← Ahora tiene ambos tags
```

## Migración Inicial

Para aplicar el sistema de tags a una base de datos existente:

```bash
python migrate_tags.py
```

Este script:
1. Crea las tablas `tags` y `user_tags`
2. Crea los tags predeterminados "IEEE Tadeo" y "IEEE YP Co"
3. Asigna el tag "IEEE Tadeo" a todos los usuarios existentes

## Visualización en la Interfaz

Los tags se muestran en la tabla de usuarios como badges de colores:

```
╔═══════════════════════════════════════════════════════════╗
║ Nombre            │ Email              │ Etiquetas       ║
╠═══════════════════════════════════════════════════════════╣
║ Erick Hansen      │ erick@elabor...   │ 🏷 IEEE Tadeo   ║
║                   │                    │ 🏷 IEEE YP Co   ║
╚═══════════════════════════════════════════════════════════╝
```

Cada badge tiene:
- Color de fondo con transparencia (color + 22)
- Borde con color más sólido (color + 44)
- Texto en el color del tag
- Tooltip con la descripción del tag

## Casos de Uso

### Caso 1: Importar usuarios de IEEE YP Colombia
```bash
# 1. Preparar CSV con usuarios de YP
# 2. Importar con tag "IEEE YP Co"
python import_users_with_tags.py usuarios_yp.csv "IEEE YP Co"

# Resultado:
# - Usuarios nuevos: creados con tag "IEEE YP Co"
# - Usuarios existentes: se les agrega "IEEE YP Co" (mantienen "IEEE Tadeo")
```

### Caso 2: Crear un nuevo tag para un evento especial
```bash
# Crear tag vía API
POST /tags/
{
  "name": "Hackathon 2025",
  "color": "#F59E0B",
  "description": "Participantes del Hackathon 2025"
}

# Importar participantes
python import_users_with_tags.py hackathon_2025.csv "Hackathon 2025"
```

### Caso 3: Filtrar usuarios por tag (futuro)
```python
# Obtener todos los usuarios con tag "IEEE YP Co"
users_yp = db.query(models.User).join(models.user_tags).join(models.Tag).filter(
    models.Tag.name == "IEEE YP Co"
).all()
```

## Notas Importantes

1. **No duplicación de tags**: El sistema verifica que un usuario no tenga el mismo tag dos veces
2. **Preservación de tags existentes**: Al importar, NUNCA se eliminan tags previos
3. **Detección por email**: Los duplicados se detectan por email (case-insensitive)
4. **Creación automática de tags**: Si el tag no existe al importar, se crea automáticamente
5. **Protección contra eliminación**: No se puede eliminar un tag si tiene usuarios asociados

## Archivos Relacionados

- `models.py` - Definición de modelos Tag y user_tags
- `schemas.py` - Esquemas Pydantic para Tag
- `main.py` - Endpoints de API para tags (líneas 325-502)
- `migrate_tags.py` - Script de migración inicial
- `import_users_with_tags.py` - Script de importación con tags
- `templates/users.html` - Visualización de tags en interfaz (líneas 121-132)

## Soporte

Para preguntas o problemas con el sistema de tags, revisar:
1. Los logs de importación (stdout del script)
2. La consola de desarrollo del navegador (F12)
3. Los logs del servidor FastAPI
