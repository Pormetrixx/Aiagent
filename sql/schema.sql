-- AI Cold Calling Agent Database Schema

-- Conversations table to store call data
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(255) UNIQUE NOT NULL,
    customer_phone VARCHAR(20),
    customer_name VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50) NOT NULL, -- 'active', 'completed', 'failed', 'abandoned'
    outcome VARCHAR(100), -- 'appointment', 'callback', 'not_interested', 'invalid_number'
    emotion_score FLOAT,
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation turns to store individual exchanges
CREATE TABLE conversation_turns (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    speaker VARCHAR(20) NOT NULL, -- 'agent' or 'customer'
    text_content TEXT NOT NULL,
    audio_file_path VARCHAR(500),
    emotion VARCHAR(50),
    confidence_score FLOAT,
    timestamp TIMESTAMP NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FAQ and knowledge base
CREATE TABLE faq_entries (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    keywords TEXT[], -- Array of keywords for matching
    usage_count INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    language VARCHAR(10) DEFAULT 'de',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation scripts and templates
CREATE TABLE conversation_scripts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    script_type VARCHAR(50) NOT NULL, -- 'opening', 'objection_handling', 'closing'
    content TEXT NOT NULL,
    variables JSONB, -- Dynamic variables in the script
    success_rate FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    language VARCHAR(10) DEFAULT 'de',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training data for continuous improvement
CREATE TABLE training_data (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    input_text TEXT NOT NULL,
    expected_response TEXT NOT NULL,
    actual_response TEXT,
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    emotion_context VARCHAR(50),
    improvement_suggestions TEXT,
    is_used_for_training BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Call outcomes and metrics
CREATE TABLE call_metrics (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type VARCHAR(50), -- 'emotion', 'sentiment', 'engagement', 'conversion'
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer information and preferences
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    preferred_language VARCHAR(10) DEFAULT 'de',
    timezone VARCHAR(50),
    best_call_time TIME,
    do_not_call BOOLEAN DEFAULT FALSE,
    notes TEXT,
    last_contact TIMESTAMP,
    conversion_probability FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configuration and settings
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(50) NOT NULL, -- 'string', 'integer', 'float', 'boolean', 'json'
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_conversations_call_id ON conversations(call_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_start_time ON conversations(start_time);
CREATE INDEX idx_conversation_turns_conversation_id ON conversation_turns(conversation_id);
CREATE INDEX idx_conversation_turns_speaker ON conversation_turns(speaker);
CREATE INDEX idx_faq_entries_category ON faq_entries(category);
CREATE INDEX idx_faq_entries_keywords ON faq_entries USING GIN(keywords);
CREATE INDEX idx_conversation_scripts_type ON conversation_scripts(script_type);
CREATE INDEX idx_training_data_conversation_id ON training_data(conversation_id);
CREATE INDEX idx_call_metrics_conversation_id ON call_metrics(conversation_id);
CREATE INDEX idx_call_metrics_metric_type ON call_metrics(metric_type);
CREATE INDEX idx_customers_phone_number ON customers(phone_number);
CREATE INDEX idx_customers_do_not_call ON customers(do_not_call);
CREATE INDEX idx_system_settings_key ON system_settings(setting_key);

-- Insert some default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_system) VALUES
('max_call_duration', '900', 'integer', 'Maximum call duration in seconds', true),
('retry_attempts', '3', 'integer', 'Number of retry attempts for failed calls', true),
('emotion_threshold', '0.7', 'float', 'Minimum confidence threshold for emotion detection', true),
('auto_training_enabled', 'true', 'boolean', 'Enable automatic training after calls', true),
('default_language', 'de', 'string', 'Default language for conversations', true);

-- Insert some sample FAQ entries
INSERT INTO faq_entries (question, answer, category, keywords) VALUES
('Was kostet Ihr Service?', 'Unsere Preise sind sehr wettbewerbsfähig. Gerne erstelle ich Ihnen ein individuelles Angebot. Wann hätten Sie Zeit für ein kurzes Gespräch?', 'pricing', ARRAY['preis', 'kosten', 'geld', 'teuer', 'billig']),
('Wie lange dauert die Umsetzung?', 'Die Umsetzungszeit hängt vom Umfang des Projekts ab. In der Regel können wir innerhalb von 2-4 Wochen starten. Soll ich Ihnen mehr Details erläutern?', 'timeline', ARRAY['zeit', 'dauer', 'schnell', 'wann', 'termin']),
('Ich habe kein Interesse', 'Das kann ich verstehen. Darf ich fragen, was für Sie momentan wichtiger ist? Vielleicht kann ich Ihnen in einem anderen Bereich helfen.', 'objection', ARRAY['kein interesse', 'nicht interessiert', 'nein danke']);

-- Insert some sample conversation scripts
INSERT INTO conversation_scripts (name, script_type, content, variables) VALUES
('Standard Opening', 'opening', 'Guten Tag, mein Name ist {agent_name} von {company_name}. Ich rufe Sie an, weil wir Unternehmen wie Ihres dabei helfen, {value_proposition}. Hätten Sie kurz Zeit für mich?', '{"agent_name": "AI Agent", "company_name": "Ihr Unternehmen", "value_proposition": "ihre Effizienz zu steigern"}'),
('Price Objection', 'objection_handling', 'Ich verstehe, dass der Preis ein wichtiger Faktor ist. Lassen Sie mich Ihnen zeigen, wie sich die Investition bereits im ersten Jahr amortisiert. Wann hätten Sie Zeit für eine kurze Präsentation?', '{}'),
('Appointment Closing', 'closing', 'Basierend auf unserem Gespräch denke ich, dass wir Ihnen wirklich helfen können. Wann wäre ein guter Zeitpunkt für ein persönliches Gespräch? Passt Ihnen {suggested_time} oder wäre {alternative_time} besser?', '{"suggested_time": "morgen um 10 Uhr", "alternative_time": "übermorgen um 14 Uhr"}');