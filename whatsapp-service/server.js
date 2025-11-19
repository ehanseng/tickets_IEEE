const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');
const cors = require('cors');
const multer = require('multer');
const sharp = require('sharp');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3010;

// Crear directorio para imágenes de WhatsApp si no existe
const WHATSAPP_IMAGES_DIR = path.join(__dirname, '../static/whatsapp_images');
fs.mkdir(WHATSAPP_IMAGES_DIR, { recursive: true }).catch(console.error);

// Configurar multer para uploads de archivos
const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 16 * 1024 * 1024 }, // 16MB max
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('Tipo de archivo no permitido. Solo imágenes.'));
        }
    }
});

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Estado del cliente
let client;
let isReady = false;
let qrCodeData = null;

// Inicializar cliente de WhatsApp
function initializeWhatsApp() {
    console.log('[INFO] Inicializando cliente de WhatsApp...');

    client = new Client({
        authStrategy: new LocalAuth({
            dataPath: './whatsapp-session'
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        }
    });

    // Evento: QR Code generado
    client.on('qr', (qr) => {
        console.log('[QR] Escanea este código QR con tu WhatsApp:');
        qrcode.generate(qr, { small: true });
        qrCodeData = qr;
        isReady = false;
    });

    // Evento: Cliente listo
    client.on('ready', () => {
        console.log('[OK] Cliente de WhatsApp está listo!');
        isReady = true;
        qrCodeData = null;
    });

    // Evento: Autenticación exitosa
    client.on('authenticated', () => {
        console.log('[OK] Autenticación exitosa');
    });

    // Evento: Error de autenticación
    client.on('auth_failure', (msg) => {
        console.error('[ERROR] Fallo en la autenticación:', msg);
        isReady = false;
    });

    // Evento: Desconectado
    client.on('disconnected', (reason) => {
        console.log('[WARN] Cliente desconectado:', reason);
        isReady = false;
        // Reintentar conexión después de 5 segundos
        setTimeout(() => {
            console.log('[INFO] Reintentando conexión...');
            client.initialize();
        }, 5000);
    });

    // Evento: Cambio de estado del mensaje (ACK)
    client.on('message_ack', async (msg, ack) => {
        try {
            const messageId = msg.id.id;
            let status = 'pending';

            // Mapear estados de ACK a nuestros estados
            switch (ack) {
                case 0: // ACK_ERROR
                    status = 'failed';
                    break;
                case 1: // ACK_PENDING
                    status = 'pending';
                    break;
                case 2: // ACK_SERVER (enviado al servidor de WhatsApp)
                    status = 'sent';
                    break;
                case 3: // ACK_DEVICE (entregado al dispositivo)
                    status = 'delivered';
                    break;
                case 4: // ACK_READ (leído por el destinatario)
                    status = 'read';
                    break;
                case 5: // ACK_PLAYED (reproducido - para audio/video)
                    status = 'read';
                    break;
            }

            console.log(`[ACK] Mensaje ${messageId} - Estado: ${status} (ACK: ${ack})`);

            // Enviar webhook a nuestro backend
            try {
                const axios = require('axios');
                await axios.post('http://localhost:8000/webhooks/whatsapp-status', {
                    message_id: messageId,
                    status: status,
                    ack: ack
                }, {
                    timeout: 5000
                });
                console.log(`[WEBHOOK] Estado enviado al backend: ${messageId} -> ${status}`);
            } catch (webhookError) {
                // No mostrar error si el backend no está disponible, solo registrar
                if (webhookError.code !== 'ECONNREFUSED') {
                    console.error(`[WEBHOOK ERROR] ${webhookError.message}`);
                }
            }
        } catch (error) {
            console.error('[ERROR] Error procesando ACK:', error);
        }
    });

    // Evento adicional: Mensaje leído (para mayor compatibilidad)
    client.on('message_revoke_everyone', async (msg) => {
        console.log(`[INFO] Mensaje revocado: ${msg.id.id}`);
    });

    // Verificar estado de mensajes periódicamente
    setInterval(async () => {
        // Este es un fallback para verificar mensajes que no recibieron ACK
        // Solo para desarrollo - en producción puede generar mucho tráfico
        console.log('[DEBUG] Verificación periódica de estados activa');
    }, 60000); // Cada minuto

    // Inicializar
    client.initialize();
}

// Rutas de la API

// GET / - Estado del servicio
app.get('/', (req, res) => {
    res.json({
        service: 'WhatsApp API Service',
        version: '1.0.0',
        status: isReady ? 'ready' : 'initializing',
        hasQR: qrCodeData !== null
    });
});

// GET /status - Estado del cliente
app.get('/status', (req, res) => {
    res.json({
        ready: isReady,
        qr: qrCodeData,
        message: isReady
            ? 'WhatsApp está conectado y listo'
            : qrCodeData
                ? 'Escanea el código QR para conectar'
                : 'Inicializando...'
    });
});

// POST /send - Enviar mensaje
app.post('/send', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado. Escanea el código QR primero.'
        });
    }

    const { phone, message } = req.body;

    if (!phone || !message) {
        return res.status(400).json({
            success: false,
            error: 'Los campos phone y message son requeridos'
        });
    }

    try {
        // Limpiar y formatear el número
        // Remover espacios, guiones, paréntesis
        let cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

        // Si no empieza con +, asumimos que ya tiene el formato correcto
        // Si empieza con +, lo dejamos así
        if (!cleanPhone.startsWith('+') && !cleanPhone.includes('@')) {
            // Si no tiene @ y no tiene +, agregamos @c.us
            cleanPhone = cleanPhone + '@c.us';
        } else if (cleanPhone.startsWith('+')) {
            // Si empieza con +, removemos el + y agregamos @c.us
            cleanPhone = cleanPhone.substring(1) + '@c.us';
        }

        console.log(`[INFO] Enviando mensaje a ${cleanPhone}`);

        // Verificar si el número existe en WhatsApp
        const isRegistered = await client.isRegisteredUser(cleanPhone);

        if (!isRegistered) {
            return res.status(404).json({
                success: false,
                error: 'Este número no está registrado en WhatsApp'
            });
        }

        // Enviar mensaje
        const result = await client.sendMessage(cleanPhone, message);

        console.log('[OK] Mensaje enviado exitosamente');

        res.json({
            success: true,
            message: 'Mensaje enviado exitosamente',
            messageId: result.id.id,
            to: cleanPhone
        });

    } catch (error) {
        console.error('[ERROR] Error al enviar mensaje:', error);
        res.status(500).json({
            success: false,
            error: 'Error al enviar mensaje: ' + error.message
        });
    }
});

// POST /send-bulk - Enviar mensajes masivos
app.post('/send-bulk', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado'
        });
    }

    const { messages } = req.body;

    if (!messages || !Array.isArray(messages)) {
        return res.status(400).json({
            success: false,
            error: 'Se requiere un array de mensajes con formato: [{phone, message}]'
        });
    }

    const results = [];

    for (const msg of messages) {
        try {
            let cleanPhone = msg.phone.replace(/[\s\-\(\)]/g, '');
            if (!cleanPhone.includes('@')) {
                cleanPhone = cleanPhone.replace('+', '') + '@c.us';
            }

            const isRegistered = await client.isRegisteredUser(cleanPhone);

            if (isRegistered) {
                await client.sendMessage(cleanPhone, msg.message);
                results.push({ phone: msg.phone, success: true });
                console.log(`[OK] Mensaje enviado a ${msg.phone}`);
            } else {
                results.push({
                    phone: msg.phone,
                    success: false,
                    error: 'No registrado en WhatsApp'
                });
            }

            // Esperar 2 segundos entre mensajes para evitar ban
            await new Promise(resolve => setTimeout(resolve, 2000));

        } catch (error) {
            results.push({
                phone: msg.phone,
                success: false,
                error: error.message
            });
            console.error(`[ERROR] Error enviando a ${msg.phone}:`, error.message);
        }
    }

    res.json({
        success: true,
        total: messages.length,
        sent: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
        results: results
    });
});

// POST /send-media - Enviar mensaje con imagen
app.post('/send-media', async (req, res) => {
    if (!isReady) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado'
        });
    }

    const { phone, message, imageBase64 } = req.body;

    if (!phone || !message || !imageBase64) {
        return res.status(400).json({
            success: false,
            error: 'Los campos phone, message e imageBase64 son requeridos'
        });
    }

    try {
        // Limpiar número de teléfono
        let cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
        if (!cleanPhone.includes('@')) {
            cleanPhone = cleanPhone.replace('+', '') + '@c.us';
        }

        console.log(`[INFO] Enviando mensaje con imagen a ${cleanPhone}`);

        // Verificar si el número existe
        const isRegistered = await client.isRegisteredUser(cleanPhone);
        if (!isRegistered) {
            return res.status(404).json({
                success: false,
                error: 'Este número no está registrado en WhatsApp'
            });
        }

        // Extraer datos de la imagen base64
        const matches = imageBase64.match(/^data:(.+);base64,(.+)$/);
        if (!matches) {
            return res.status(400).json({
                success: false,
                error: 'Formato de imagen base64 inválido'
            });
        }

        const mimeType = matches[1];
        const base64Data = matches[2];
        const imageBuffer = Buffer.from(base64Data, 'base64');

        // Comprimir imagen con sharp (optimizar para WhatsApp)
        const compressedBuffer = await sharp(imageBuffer)
            .resize(1200, 1200, {
                fit: 'inside',
                withoutEnlargement: true
            })
            .jpeg({
                quality: 85,
                progressive: true
            })
            .toBuffer();

        // Guardar imagen comprimida
        const timestamp = Date.now();
        const filename = `wa_${timestamp}.jpg`;
        const filepath = path.join(WHATSAPP_IMAGES_DIR, filename);
        await fs.writeFile(filepath, compressedBuffer);

        console.log(`[INFO] Imagen guardada y comprimida: ${filename}`);
        console.log(`[INFO] Tamaño original: ${(imageBuffer.length / 1024).toFixed(2)}KB`);
        console.log(`[INFO] Tamaño comprimido: ${(compressedBuffer.length / 1024).toFixed(2)}KB`);

        // Crear objeto MessageMedia
        const media = MessageMedia.fromFilePath(filepath);

        // Enviar mensaje con imagen
        const result = await client.sendMessage(cleanPhone, media, { caption: message });

        console.log('[OK] Mensaje con imagen enviado exitosamente');

        // Limpiar archivo temporal después de 30 segundos
        setTimeout(async () => {
            try {
                await fs.unlink(filepath);
                console.log(`[INFO] Archivo temporal eliminado: ${filename}`);
            } catch (err) {
                console.error(`[WARN] No se pudo eliminar archivo temporal: ${err.message}`);
            }
        }, 30000);

        res.json({
            success: true,
            message: 'Mensaje con imagen enviado exitosamente',
            messageId: result.id.id,
            to: cleanPhone,
            imageCompression: {
                originalSize: `${(imageBuffer.length / 1024).toFixed(2)}KB`,
                compressedSize: `${(compressedBuffer.length / 1024).toFixed(2)}KB`
            }
        });

    } catch (error) {
        console.error('[ERROR] Error al enviar mensaje con imagen:', error);
        res.status(500).json({
            success: false,
            error: 'Error al enviar mensaje: ' + error.message
        });
    }
});

// POST /restart - Reiniciar cliente (útil si se pierde conexión)
app.post('/restart', async (req, res) => {
    console.log('[INFO] Reiniciando cliente...');

    try {
        if (client) {
            console.log('[INFO] Destruyendo cliente existente...');
            await client.destroy();
        }

        // Resetear estado
        isReady = false;
        qrCodeData = null;

        // Esperar un momento para que se limpie todo
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log('[INFO] Inicializando nuevo cliente...');
        initializeWhatsApp();

        res.json({
            success: true,
            message: 'Cliente reiniciado. Escanea el código QR si es necesario.'
        });
    } catch (error) {
        console.error('[ERROR] Error al reiniciar cliente:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// POST /logout - Cerrar sesión y eliminar credenciales
app.post('/logout', async (req, res) => {
    console.log('[INFO] Cerrando sesión y eliminando credenciales...');

    try {
        if (client) {
            console.log('[INFO] Destruyendo cliente...');
            await client.destroy();
        }

        // Resetear estado
        isReady = false;
        qrCodeData = null;

        // Eliminar directorio de sesión
        const sessionPath = path.join(__dirname, 'whatsapp-session');
        console.log('[INFO] Eliminando directorio de sesión:', sessionPath);

        try {
            await fs.rm(sessionPath, { recursive: true, force: true });
            console.log('[OK] Directorio de sesión eliminado');
        } catch (err) {
            console.warn('[WARN] No se pudo eliminar directorio de sesión:', err.message);
        }

        // Esperar un momento
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Reinicializar para generar nuevo QR
        console.log('[INFO] Inicializando nuevo cliente...');
        initializeWhatsApp();

        res.json({
            success: true,
            message: 'Sesión cerrada. Escanea el nuevo código QR con el número deseado.'
        });
    } catch (error) {
        console.error('[ERROR] Error al cerrar sesión:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`[OK] Servidor WhatsApp API corriendo en http://localhost:${PORT}`);
    console.log('[INFO] Endpoints disponibles:');
    console.log('  GET  / - Estado del servicio');
    console.log('  GET  /status - Estado de conexión y QR');
    console.log('  POST /send - Enviar mensaje individual');
    console.log('  POST /send-media - Enviar mensaje con imagen');
    console.log('  POST /send-bulk - Enviar mensajes masivos');
    console.log('  POST /restart - Reiniciar cliente (mantiene sesión)');
    console.log('  POST /logout - Cerrar sesión y generar nuevo QR');
    console.log('');

    // Inicializar WhatsApp
    initializeWhatsApp();
});

// Manejo de errores no capturados
process.on('unhandledRejection', (error) => {
    console.error('[ERROR] Unhandled rejection:', error);
});

process.on('uncaughtException', (error) => {
    console.error('[ERROR] Uncaught exception:', error);
});
