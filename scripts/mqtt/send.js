#!/usr/bin/env node
/**
 * Send a message to another bot via MQTT
 * Usage: send.js <target-bot> <message>
 * Example: send.js magi "Hey, can you check the backups?"
 */

const mqtt = require('mqtt');

const BOT_NAME = process.env.BOT_NAME || 'marvin';
const MQTT_BROKER = process.env.MQTT_BROKER || 'mqtt://192.168.1.151:1883';
const MQTT_USER = process.env.MQTT_USER || 'mqtt';
const MQTT_PASS = process.env.MQTT_PASS || 'letx';

const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: send.js <target-bot> <message>');
  console.error('Example: send.js magi "Check the backups please"');
  process.exit(1);
}

const targetBot = args[0];
const messageText = args.slice(1).join(' ');
const topic = `bots/${targetBot}/inbox`;

const message = {
  id: `${BOT_NAME}-${Date.now()}`,
  from: BOT_NAME,
  to: targetBot,
  type: 'message',
  text: messageText,
  timestamp: new Date().toISOString(),
  replyTo: `bots/${BOT_NAME}/inbox`
};

const client = mqtt.connect(MQTT_BROKER, {
  username: MQTT_USER,
  password: MQTT_PASS,
  clientId: `${BOT_NAME}-sender-${Date.now()}`
});

client.on('connect', () => {
  client.publish(topic, JSON.stringify(message), { qos: 1 }, (err) => {
    if (err) {
      console.error(`Failed to send: ${err.message}`);
      process.exit(1);
    }
    console.log(`✓ Sent to ${targetBot}: "${messageText}"`);
    client.end();
    process.exit(0);
  });
});

client.on('error', (err) => {
  console.error(`MQTT Error: ${err.message}`);
  process.exit(1);
});

// Timeout after 10 seconds
setTimeout(() => {
  console.error('Timeout connecting to MQTT broker');
  process.exit(1);
}, 10000);
