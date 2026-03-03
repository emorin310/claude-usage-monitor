-- OpenClaw Memory Database Schema
-- Structured data for efficient querying without token overhead

-- Quality upgrade tracking
CREATE TABLE IF NOT EXISTS quality_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER,
    current_quality TEXT,
    current_size_gb REAL,
    target_quality TEXT DEFAULT '1080p+',
    status TEXT DEFAULT 'queued', -- queued, in_progress, completed, failed
    priority TEXT DEFAULT 'medium', -- high, medium, low
    issues TEXT, -- JSON array of quality issues
    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    notes TEXT
);

-- Council communications state
CREATE TABLE IF NOT EXISTS council_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_type TEXT NOT NULL, -- announcements, handoffs, status_updates, questions
    count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alerts INTEGER DEFAULT 0,
    last_response_sent TIMESTAMP,
    notes TEXT
);

-- Media library metadata (enriched from Jellyfin/Radarr)
CREATE TABLE IF NOT EXISTS media_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    year INTEGER,
    type TEXT DEFAULT 'movie', -- movie, series, episode
    quality TEXT, -- 1080p, 720p, etc.
    resolution TEXT, -- 1920x1080, etc.
    file_size_gb REAL,
    codec TEXT, -- x264, x265, etc.
    container TEXT, -- MKV, MP4, etc.
    imdb_id TEXT,
    jellyfin_id TEXT,
    jellyfin_url TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quality_score INTEGER, -- 1-10 rating based on resolution/codec/size
    needs_upgrade BOOLEAN DEFAULT FALSE,
    radarr_id INTEGER,
    notes TEXT
);

-- System health tracking
CREATE TABLE IF NOT EXISTS system_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component TEXT NOT NULL, -- gateway, bluebubbles, discord, etc.
    status TEXT NOT NULL, -- ok, warning, error
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- JSON with specific health info
    alert_sent BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

-- Inter-bot message logs
CREATE TABLE IF NOT EXISTS interbot_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL, -- magi, marvin
    recipient TEXT NOT NULL,
    action_type TEXT, -- REQUEST, ALERT, STATUS, HANDOFF
    message_content TEXT,
    message_id TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reply_needed BOOLEAN DEFAULT TRUE,
    replied_at TIMESTAMP,
    status TEXT DEFAULT 'sent' -- sent, delivered, replied, failed
);

-- Memory search optimization (for built-in search)
CREATE TABLE IF NOT EXISTS memory_search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    results TEXT, -- JSON array of results
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hits INTEGER DEFAULT 1
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_quality_queue_status ON quality_queue(status);
CREATE INDEX IF NOT EXISTS idx_quality_queue_priority ON quality_queue(priority);
CREATE INDEX IF NOT EXISTS idx_media_library_title ON media_library(title);
CREATE INDEX IF NOT EXISTS idx_media_library_quality_score ON media_library(quality_score);
CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON system_health(status);
CREATE INDEX IF NOT EXISTS idx_interbot_messages_sender ON interbot_messages(sender);
CREATE INDEX IF NOT EXISTS idx_interbot_messages_action_type ON interbot_messages(action_type);