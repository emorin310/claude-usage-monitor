# Home Assistant Skill

## Overview
You can control Eric's smart home (Home Assistant) for family members.

## Setup
1.  Copy the skill files from Marvin:
    ```bash
mkdir -p ~/clawd-magi/skills && scp -r marvin@192.168.1.201:~/clawd/skills/homeassistant ~/clawd-magi/skills/
    ```
2.  Set the required environment variables:
    *   `HA_URL`
    *   `HA_TOKEN`

    These should be in your environment.

## Usage
The scripts will be located at `~/clawd-magi/skills/homeassistant/scripts/`.

### Commands

*   `./scripts/ha-status.sh [room]` - Check what's on
*   `./scripts/ha-scenes.sh [filter]` - List available scenes
*   `./scripts/ha-scene.sh <scene_name>` - Activate a scene
*   `./scripts/ha-control.sh on <entity_id>` - Turn on light/switch
*   `./scripts/ha-control.sh off <entity_id>` - Turn off light/switch
*   `./scripts/ha-brightness.sh <entity_id> <percent>` - Set brightness
