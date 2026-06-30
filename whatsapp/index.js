const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys')
const { Boom } = require('@hapi/boom')
const express = require('express')
const axios = require('axios')
const path = require('path')
const qrcode = require('qrcode-terminal')

const app = express()
app.use(express.json({ limit: '50mb' }))

const N8N_WEBHOOK = 'http://127.0.0.1:5678/webhook/cs-lite'
const SESSION_DIR = path.join(__dirname, 'sessions')
const PORT = 3000

let sock = null
let isConnected = false

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(SESSION_DIR)
    const { version } = await fetchLatestBaileysVersion()

    sock = makeWASocket({
        version,
        auth: state,
        browser: ['CS-AI', 'Chrome', '1.0'],
        syncFullHistory: false
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', ({ connection, lastDisconnect, qr }) => {
        if (qr) {
            console.log('\n📱 Scan this QR code with WhatsApp:\n')
            qrcode.generate(qr, { small: true })
        }
        if (connection === 'close') {
            isConnected = false
            const statusCode = new Boom(lastDisconnect?.error)?.output?.statusCode
            if (statusCode !== DisconnectReason.loggedOut) {
                console.log('🔄 Reconnecting...')
                connectToWhatsApp()
            } else {
                console.log('❌ Logged out. Delete the sessions folder and restart.')
            }
        } else if (connection === 'open') {
            isConnected = true
            console.log('✅ WhatsApp connected!')
        }
    })

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return

        for (const msg of messages) {
            if (msg.key.fromMe) continue
            if (!msg.message) continue

            const jid = msg.key.remoteJid
            if (jid.endsWith('@g.us')) continue  // ignore group messages

            const phone = jid.replace('@s.whatsapp.net', '')
            const text = msg.message?.conversation
                || msg.message?.extendedTextMessage?.text
                || ''
            const name = msg.pushName || phone

            if (!text.trim()) continue

            console.log(`📩 [${phone}] ${name}: ${text}`)

            try {
                await axios.post(N8N_WEBHOOK, { phone, text, name }, { timeout: 30000 })
            } catch (err) {
                console.error(`❌ n8n error: ${err.message}`)
            }
        }
    })
}

// Send text
app.post('/send', async (req, res) => {
    const { phone, text } = req.body
    console.log(`📤 /send → phone=${phone}, text=${text?.substring(0,50)}`)
    if (!isConnected) return res.status(500).json({ ok: false, error: 'WhatsApp not connected' })
    if (!phone || !text) return res.status(400).json({ ok: false, error: 'Missing phone or text' })
    try {
        const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
        await sock.sendMessage(jid, { text: String(text) })
        res.json({ ok: true })
    } catch (err) {
        console.error('Send error:', err.message)
        res.status(500).json({ ok: false, error: err.message })
    }
})

// Send PDF document
app.post('/send-document', async (req, res) => {
    const { phone, base64, filename } = req.body
    console.log(`📎 /send-document → phone=${phone}, filename=${filename}`)
    if (!isConnected) return res.status(500).json({ ok: false, error: 'WhatsApp not connected' })
    if (!phone || !base64) return res.status(400).json({ ok: false, error: 'Missing phone or base64' })

    // Return immediately, send in background
    res.json({ ok: true })

    try {
        const buffer = Buffer.from(base64, 'base64')
        const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
        console.log(`📎 Sending PDF ${buffer.length} bytes to ${jid}`)
        await sock.sendMessage(jid, {
            document: buffer,
            fileName: filename || 'quotation.pdf',
            mimetype: 'application/pdf',
            caption: '📄 Here is your personalised quotation!'
        })
        console.log(`✅ PDF sent to ${jid}`)
    } catch (err) {
        console.error(`❌ PDF send error: ${err.message}`)
    }
})

// Health check
app.get('/health', (req, res) => {
    res.json({ ok: true, connected: isConnected })
})

app.listen(PORT, () => {
    console.log(`✅ WhatsApp service running on http://127.0.0.1:${PORT}`)
    console.log('📱 Scan QR code below to connect WhatsApp...')
})

connectToWhatsApp()
