# Optimización de Envío Masivo de WhatsApp

## Problema Identificado

El sistema colapsaba durante el envío masivo de mensajes por WhatsApp debido a:

1. **Sobrecarga del servidor de WhatsApp** (puerto 3010)
2. **Rate limiting de WhatsApp Web**
3. **Falta de control de flujo**
4. **Envío sin pausas entre mensajes**

## Solución Implementada

### 1. Delays Progresivos

Se implementó un sistema de delays progresivos entre mensajes para evitar saturar el servicio:

```python
# Delay progresivo entre mensajes
base_delay = 2.0  # 2 segundos base
extra_delay = (idx // 10) * 0.5  # +0.5s cada 10 mensajes
total_delay = min(base_delay + extra_delay, 5.0)  # Máximo 5 segundos
```

**Ejemplo de tiempos de espera:**
- Mensajes 1-10: 2.0 segundos
- Mensajes 11-20: 2.5 segundos
- Mensajes 21-30: 3.0 segundos
- Mensajes 31-40: 3.5 segundos
- Mensajes 41-50: 4.0 segundos
- Mensajes 51+: 4.5 segundos
- Máximo: 5.0 segundos

### 2. Archivos Modificados

#### main.py - Línea 1685-1741
**Endpoint:** `/tickets/send-whatsapp-by-event`
- Envío masivo de tickets por evento
- Delay implementado entre cada ticket enviado

#### main.py - Línea 2267-2356
**Endpoint:** `/messages/send-bulk`
- Envío de campañas masivas de mensajes
- Delay implementado solo cuando se envía por WhatsApp

### 3. Beneficios

✅ **Previene colapso del servidor**: El delay evita saturar el servicio de WhatsApp
✅ **Respeta límites de WhatsApp**: Rate limiting más conservador
✅ **Mejor manejo de errores**: Reduce errores de timeout
✅ **Escalable**: El delay aumenta progresivamente con más mensajes
✅ **No afecta emails**: Los delays solo se aplican a WhatsApp

### 4. Tiempos Estimados de Envío

Para diferentes cantidades de mensajes:

| Mensajes | Tiempo Estimado | Delay Promedio |
|----------|----------------|----------------|
| 10       | ~20 segundos   | 2.0s           |
| 25       | ~65 segundos   | 2.6s           |
| 50       | ~3.5 minutos   | 4.2s           |
| 100      | ~7.5 minutos   | 4.5s           |
| 200      | ~15 minutos    | 4.5s           |

**Nota:** Estos tiempos son aproximados y no incluyen el tiempo de procesamiento del mensaje en el servidor de WhatsApp.

### 5. Recomendaciones Adicionales

#### A. Monitorear el Servicio de WhatsApp

```bash
# Ver estado del servicio
curl http://localhost:3010/status

# Ver logs del servicio
# (en la ventana donde corre el servicio de WhatsApp)
```

#### B. Si el Sistema Sigue Colapsando

1. **Aumentar el delay base**:
   ```python
   base_delay = 3.0  # Aumentar de 2.0 a 3.0
   ```

2. **Reducir el máximo de mensajes por lote**:
   - Dividir envíos grandes en múltiples sesiones
   - Por ejemplo: 100 mensajes en 2 lotes de 50

3. **Reiniciar el servicio de WhatsApp**:
   ```bash
   # Desde el panel de admin o manualmente
   curl -X POST http://localhost:3010/restart
   ```

#### C. Mejoras Futuras Potenciales

1. **Cola de mensajes con Celery/Redis**: Procesamiento asíncrono
2. **Múltiples instancias de WhatsApp**: Balanceo de carga
3. **Monitoreo en tiempo real**: Dashboard de estado
4. **Retry automático**: Reintentos con backoff exponencial
5. **Límite configurable**: Permitir ajustar delays desde la UI

### 6. Troubleshooting

#### Problema: "WhatsApp service not ready"
**Solución:**
1. Verificar que el servicio esté corriendo en puerto 3010
2. Verificar que la sesión de WhatsApp esté activa
3. Reiniciar el servicio si es necesario

#### Problema: Mensajes lentos pero sin errores
**Solución:**
- Esto es normal con el delay implementado
- El sistema prioriza estabilidad sobre velocidad
- Para envíos urgentes, considera dividir en lotes más pequeños

#### Problema: Algunos mensajes no se envían
**Solución:**
1. Revisar los errores específicos en el resultado
2. Verificar números de teléfono válidos
3. Comprobar límites diarios de WhatsApp
4. Verificar que la cuenta de WhatsApp no esté bloqueada

## Changelog

### v1.1 - 2025-11-20
- ✅ Implementado delay progresivo en envío de tickets
- ✅ Implementado delay progresivo en campañas masivas
- ✅ Documentación de optimizaciones
- ✅ Ejemplos de uso y troubleshooting
