const { Client, LocalAuth } = require('whatsapp-web.js');
const express = require('express');
const qrcode = require('qrcode-terminal');
const cors = require('cors');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

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

// POST /restart - Reiniciar cliente (útil si se pierde conexión)
app.post('/restart', async (req, res) => {
    console.log('[INFO] Reiniciando cliente...');

    if (client) {
        await client.destroy();
    }

    initializeWhatsApp();

    res.json({
        success: true,
        message: 'Cliente reiniciado. Escanea el código QR si es necesario.'
    });
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`[OK] Servidor WhatsApp API corriendo en http://localhost:${PORT}`);
    console.log('[INFO] Endpoints disponibles:');
    console.log('  GET  / - Estado del servicio');
    console.log('  GET  /status - Estado de conexión y QR');
    console.log('  POST /send - Enviar mensaje individual');
    console.log('  POST /send-bulk - Enviar mensajes masivos');
    console.log('  POST /restart - Reiniciar cliente');
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
