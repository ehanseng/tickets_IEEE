# Configuración para Claude Code

## Servidor de Despliegue

- **Host**: 192.168.1.85 (red local)
- **Usuario**: shareloc
- **Ruta del proyecto**: /home/shareloc/ieeetadeo/
- **Servicio**: ieeetadeo (systemd)

## Comandos de Despliegue

### Subir archivo individual:
```bash
scp "archivo_local" shareloc@192.168.1.85:/home/shareloc/ieeetadeo/archivo_destino
```

### Subir template:
```bash
scp "templates/archivo.html" shareloc@192.168.1.85:/home/shareloc/ieeetadeo/templates/
```

### Reiniciar servicio:
```bash
ssh shareloc@192.168.1.85 "sudo systemctl restart ieeetadeo"
```

### Deploy completo (archivo + reinicio):
```bash
scp "archivo" shareloc@192.168.1.85:/home/shareloc/ieeetadeo/ && ssh shareloc@192.168.1.85 "sudo systemctl restart ieeetadeo"
```

## Base de Datos

- **Motor**: MySQL
- **Host**: Configurado en .env del servidor
- **Base de datos**: ieeetadeo

## Notas

- NO usar IP 64.23.150.20 (esa es otra cosa)
- NO usar usuario root, siempre shareloc
- La autenticación SSH es por clave pública (ya configurada)
