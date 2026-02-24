# Smart Home Skill - Magi Edition

Control Eric's smart home via Home Assistant (hal). Safe for family use.

## Setup

Copy skill to magrathea:
```bash
mkdir -p ~/clawd-magi/skills
scp -r marvin@192.168.1.201:~/clawd/skills/homeassistant ~/clawd-magi/skills/
```

Scripts will be at: `~/clawd-magi/skills/homeassistant/scripts/`

## Environment Variables
```bash
export HA_URL="http://192.168.1.151:8123"
export HA_TOKEN="<long-lived-access-token>"
```

## Safe Commands (Magi Can Run Directly)

### List Available Scenes
```bash
./ha-scenes.sh
```
Shows all scenes users can activate.

### Get Room/Entity Status
```bash
./ha-status.sh [room|entity]
# Examples:
./ha-status.sh              # All controllable entities
./ha-status.sh office       # Office lights/switches
./ha-status.sh light.deck   # Specific entity
```

### Turn On/Off Lights or Switches
```bash
./ha-control.sh on <entity_id>
./ha-control.sh off <entity_id>
./ha-control.sh toggle <entity_id>

# Examples:
./ha-control.sh on light.deck_ceiling_switch
./ha-control.sh off light.sunroom_string_lights
```

### Activate Scene
```bash
./ha-scene.sh <scene_name>
# Examples:
./ha-scene.sh office_evening
./ha-scene.sh master_all_off
./ha-scene.sh deck_evening
```

### Set Light Brightness
```bash
./ha-brightness.sh <entity_id> <percent>
# Example:
./ha-brightness.sh light.guest_bedroom_aux_lighting 50
```

## Common User Requests → Commands

| User Says | Command |
|-----------|---------|
| "Turn on the deck lights" | `./ha-control.sh on light.deck_ceiling_switch` |
| "Turn off all office lights" | `./ha-scene.sh office_lights_out` |
| "Movie mode" / "dim the office" | `./ha-scene.sh office_lights_dimmed` |
| "Bedtime" | `./ha-scene.sh master_all_off` |
| "What's on?" | `./ha-status.sh` |
| "Is the deck light on?" | `./ha-status.sh deck` |

## Room/Area Keywords

Map user language to entity patterns:
- **office** → `light.*office*`, `switch.*office*`
- **deck** → `light.*deck*`
- **master/bedroom** → `*master*`
- **guest** → `*guest*`
- **basement** → `*basement*`
- **sunroom** → `*sunroom*`
- **gym** → `*gym*`
- **front yard** → `*front_yard*`

## Available Scenes (Quick Reference)

**Office:**
- `office_daytime` - Bright work lighting
- `office_evening` - Warm evening lighting  
- `office_lights_dimmed` - Dimmed/movie mode
- `office_lights_out` - All office lights off

**Master Bedroom:**
- `master_all_on` - All master lights on
- `master_evening` - Evening ambiance
- `master_all_off` - All off (bedtime)

**Deck/Outside:**
- `deck_evening` - Deck evening ambiance
- `deck_lights_out` - Deck off
- `front_yard_evening` - Front yard evening
- `outside` - Outside lights off

**Basement:**
- `basement_evening` - Basement evening
- `basement_brightest` - Full brightness
- `basement_off` - Basement off

**Gym:**
- `gym_evening`, `gym_daytime`, `gym_night`, `gym_lights_out`

## Response Examples

**Turning on a light:**
```json
{"status":"SUCCESS","entity":"light.deck_ceiling_switch","action":"turn_on","new_state":"on"}
```
→ "Done! The deck ceiling light is now on."

**Activating a scene:**
```json
{"status":"SUCCESS","scene":"office_evening","message":"Scene activated"}
```
→ "I've set the office to evening mode."

**Status check:**
```json
{"entity":"light.deck_ceiling_switch","state":"on","friendly_name":"deck ceiling switch","brightness":255}
```
→ "The deck ceiling light is on at full brightness."

## Safety Notes

- All commands are **reversible** (on/off, scenes)
- No **destructive** operations
- No access to **security** entities (alarm, locks)
- Climate control limited to **reasonable ranges** (60-80°F)

## Error Handling

- **Entity not found**: Suggest similar entities
- **Service unavailable**: "Home Assistant isn't responding - try again in a moment"
- **Invalid command**: Show available options
