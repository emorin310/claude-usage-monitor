#!/usr/bin/env node
/**
 * MQTT Listener Daemon
 * Subscribes to bots/{botname}/inbox and triggers OpenClaw session on messages
 */

const mqtt = require('mqtt');
const { execSync, spawn } = require('child_process');
const fs = require('fs');

// Config
const BOT_NAME = process.env.BOT_NAME || 'marvin';
const MQTT_BROKER = process.env.MQTT_BROKER || 'mqtt://192.168.1.151:1883';
const MQTT_USER = process.env.MQTT_USER || 'mqtt';
const MQTT_PASS = process.env.MQTT_PASS || 'letx';
const INBOX_TOPIC = `bots/${BOT_NAME}/inbox`;
const STATUS_TOPIC = `bots/${BOT_NAME}/status`;
const LOG_FILE = process.env.LOG_FILE || `/tmp/mqtt-listener-${BOT_NAME}.log`;

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}`;
  console.log(line);
  fs.appendFileSync(LOG_FILE, line + '\n');
}

function sendToOpenClaw(message) {
  try {
    const text = message.text || message.toString();
    const from = message.from || 'unknown';
    const replyTo = message.replyTo || `bots/${from}/inbox`;
    
    // Use Discord #council-comms with @mention to trigger the target bot
    const COUNCIL_CHANNEL = '1475399300421914766';
    
    // Bot IDs for mentions
    const BOT_IDS = {
      'marvin': '<@1475401340765147319>',
      'magi': '<@1475366845602332732>'
    };
    
    const targetMention = BOT_IDS[BOT_NAME] || `@${BOT_NAME}`;
    
    // Format with @mention to trigger the target bot
    const discordMsg = `${targetMention} 📨 **Inter-bot message from ${from}:**\n\n${text}\n\n_Reply using: \`node ~/clawd/scripts/mqtt/send.js ${from} "your response"\`_`;
    
    log(`Posting to Discord #council-comms with mention for ${BOT_NAME}`);
    
    // Use openclaw message command to post to Discord
    const child = spawn('openclaw', [
      'message', 'send',
      '--channel', 'discord',
      '--target', `channel:${COUNCIL_CHANNEL}`,
      '--message', discordMsg
    ], {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, HOME: process.env.HOME || '/home/' + BOT_NAME }
    });
    
    child.stdout.on('data', (data) => log(`message stdout: ${data}`));
    child.stderr.on('data', (data) => log(`message stderr: ${data}`));
    child.on('close', (code) => log(`message exited with code ${code}`));
    child.unref();
    
    log(`Posted Discord mention for ${BOT_NAME} from ${from}`);
    return true;
  } catch (err) {
    log(`ERROR posting to Discord: ${err.message}`);
    return false;
  }
}

// Connect to MQTT
log(`Connecting to ${MQTT_BROKER} as ${BOT_NAME}...`);

const client = mqtt.connect(MQTT_BROKER, {
  username: MQTT_USER,
  password: MQTT_PASS,
  clientId: `${BOT_NAME}-listener-${Date.now()}`,
  reconnectPeriod: 5000,
  keepalive: 60
});

client.on('connect', () => {
  log(`Connected to MQTT broker`);
  
  // Subscribe to inbox
  client.subscribe(INBOX_TOPIC, { qos: 1 }, (err) => {
    if (err) {
      log(`ERROR subscribing to ${INBOX_TOPIC}: ${err.message}`);
    } else {
      log(`Subscribed to ${INBOX_TOPIC}`);
    }
  });
  
  // Publish online status
  client.publish(STATUS_TOPIC, JSON.stringify({
    status: 'online',
    listener: true,
    timestamp: new Date().toISOString()
  }), { retain: true });
});

client.on('message', (topic, payload) => {
  log(`Received message on ${topic}`);
  
  try {
    const message = JSON.parse(payload.toString());
    log(`From: ${message.from}, Type: ${message.type || 'message'}`);
    
    // Ignore our own messages
    if (message.from === BOT_NAME) {
      log('Ignoring own message');
      return;
    }
    
    // Handle based on type
    if (message.type === 'ping') {
      // Respond to pings
      const replyTopic = `bots/${message.from}/inbox`;
      client.publish(replyTopic, JSON.stringify({
        from: BOT_NAME,
        type: 'pong',
        replyTo: message.id,
        timestamp: new Date().toISOString()
      }));
      log(`Sent pong to ${message.from}`);
    } else {
      // Forward to OpenClaw
      sendToOpenClaw(message);
    }
  } catch (err) {
    log(`ERROR parsing message: ${err.message}`);
    // Try sending raw payload to OpenClaw
    sendToOpenClaw({ text: payload.toString(), from: 'unknown' });
  }
});

client.on('error', (err) => {
  log(`MQTT Error: ${err.message}`);
});

client.on('offline', () => {
  log('MQTT client offline');
});

client.on('reconnect', () => {
  log('Reconnecting to MQTT...');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  log('Received SIGTERM, shutting down...');
  client.publish(STATUS_TOPIC, JSON.stringify({
    status: 'offline',
    timestamp: new Date().toISOString()
  }), { retain: true }, () => {
    client.end();
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  log('Received SIGINT, shutting down...');
  client.end();
  process.exit(0);
});

log(`MQTT Listener started for ${BOT_NAME}`);
