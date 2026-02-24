# Media Request Skill - Magi Edition

Fast, local media library queries for family requests.

## Setup

Copy scripts to magrathea:
```bash
scp -r marvin@192.168.1.201:~/clawd/skills/media-request/scripts ~/skills/media-request/
```

Or clone from the skill directory.

## Environment Variables
```bash
export RADARR_URL="http://10.15.40.89:7878"
export RADARR_KEY="9357c52a8209410cbfabb2cdad6480bf"
export SONARR_URL="http://10.15.40.89:8989"
export SONARR_KEY="09998432e0ec46e590ac9ff9235b4229"
export JELLYFIN_URL="http://192.168.1.96:8096"
export JELLYFIN_KEY="c5b4d7fc157b49778470414e5944b0b2"
export JELLYFIN_PUBLIC="https://jellyfin.ericmorin.online"
```

## Commands Magi Can Run Directly (Read-Only)

### Search Library
```bash
./search-library.sh "movie name" [movie|tv|all]
```
Returns: titles, poster URLs, Jellyfin play links, IMDB links

### Search TMDB (for things not in library)
```bash
./search-tmdb.sh "movie name" [movie|tv]
```
Returns: TMDB results with posters, IMDB links, "inLibrary" flag

### Library Stats
```bash
./library-stats.sh
```
Returns: movie/TV counts, storage size

### Weekly Watch Stats
```bash
./weekly-stats.sh [days]
```
Returns: plays, top watched, recently added

### Quick Connect Auth
```bash
./jellyfin-quickconnect.sh <code>
```
Authorizes Jellyfin login code

## Commands to Route Through Marvin (Write Operations)

### Request Movie
Send via MQTT to `bots/marvin/inbox`:
```json
{
  "from": "magi",
  "payload": {
    "action": "request_movie",
    "title": "Movie Name",
    "year": 2024,
    "requestedBy": "Username",
    "replySession": "magi"
  }
}
```

Marvin will:
1. Add to Radarr
2. Track download progress
3. Notify Magi when complete via `bots/magi/inbox`

## MQTT Quick Reference
```bash
# Broker: 192.168.1.151:1883 (HA Mosquitto)
# Credentials: mqtt / letx

# Send to Marvin
mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/marvin/inbox" -m '{"from":"magi","payload":{...}}'

# Listen for responses
mosquitto_sub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/magi/inbox"
```

## Example Responses

### Library Search Result
```json
{
  "status": "FOUND",
  "results": [{
    "title": "Paddington",
    "year": 2014,
    "posterUrl": "https://image.tmdb.org/t/p/w500/...",
    "playUrl": "https://jellyfin.ericmorin.online/web/...#!/details?id=...",
    "imdbUrl": "https://www.imdb.com/title/tt1109624/"
  }]
}
```

### Not in Library
```json
{
  "status": "NOT_FOUND",
  "query": "Some Movie",
  "message": "No matches in library"
}
```
→ Offer to request it (route through Marvin)

## User Flow Examples

**"Do we have Paddington?"**
→ Run `search-library.sh "Paddington"`
→ Return poster + "Yes! [Play in Jellyfin]"

**"Can we watch Arrival?"**
→ Run `search-library.sh "Arrival"`
→ If NOT_FOUND: Run `search-tmdb.sh "Arrival"`
→ Show poster + "Not in library. Want me to request it?"
→ If yes: MQTT to Marvin

**"What did we watch this week?"**
→ Run `weekly-stats.sh 7`
→ Format top watched list

**"I need to log in" + code**
→ Run `jellyfin-quickconnect.sh <code>`
→ "You're in!"
