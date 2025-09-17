<?php
// Database configuration and connection helper
class DatabaseHelper {
    private $pdo;
    private $config;
    
    public function __construct() {
        $this->config = [
            'host' => $_ENV['DB_HOST'] ?? 'localhost',
            'dbname' => $_ENV['DB_NAME'] ?? 'aiagent',
            'username' => $_ENV['DB_USER'] ?? 'aiagent_user',
            'password' => $_ENV['DB_PASS'] ?? 'aiagent_pass'
        ];
        
        $this->connect();
    }
    
    private function connect() {
        try {
            $dsn = "mysql:host={$this->config['host']};dbname={$this->config['dbname']};charset=utf8mb4";
            $this->pdo = new PDO($dsn, $this->config['username'], $this->config['password'], [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false
            ]);
        } catch (PDOException $e) {
            // Fallback to SQLite for development
            try {
                $this->pdo = new PDO('sqlite:' . __DIR__ . '/aiagent.db');
                $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                $this->createSQLiteTables();
            } catch (PDOException $e2) {
                throw new Exception('Database connection failed: ' . $e2->getMessage());
            }
        }
    }
    
    private function createSQLiteTables() {
        $tables = [
            'scripts' => "
                CREATE TABLE IF NOT EXISTS scripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    context TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ",
            'faqs' => "
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ",
            'customers' => "
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    email TEXT,
                    company TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ",
            'calls' => "
                CREATE TABLE IF NOT EXISTS calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    phone TEXT NOT NULL,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    duration INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'initiated',
                    notes TEXT,
                    recording_path TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(id)
                )
            "
        ];
        
        foreach ($tables as $sql) {
            $this->pdo->exec($sql);
        }
        
        // Insert sample data if tables are empty
        $this->insertSampleData();
    }
    
    private function insertSampleData() {
        // Check if we have any scripts
        $count = $this->pdo->query("SELECT COUNT(*) FROM scripts")->fetchColumn();
        if ($count == 0) {
            $sampleData = [
                "INSERT INTO scripts (name, context, content) VALUES 
                    ('Default Opening', 'opening', 'Hello, this is the AI Cold Calling Agent. How are you today?'),
                    ('Price Objection', 'objection_handling', 'I understand price is important. Let me explain the value we provide...'),
                    ('Closing Question', 'closing', 'Based on our conversation, would you be interested in scheduling a follow-up meeting?')",
                
                "INSERT INTO faqs (question, answer, category) VALUES 
                    ('What is your pricing?', 'Our pricing starts at €99/month for the basic package, which includes unlimited calls and basic analytics.', 'pricing'),
                    ('Do you offer support?', 'Yes, we provide 24/7 customer support via phone and email, plus comprehensive documentation.', 'support'),
                    ('How does the AI work?', 'Our AI uses advanced natural language processing to conduct professional sales conversations.', 'technical')",
                
                "INSERT INTO customers (name, phone, email, company) VALUES 
                    ('John Doe', '+49123456789', 'john@example.com', 'Example Corp'),
                    ('Jane Smith', '+49987654321', 'jane@test.com', 'Test GmbH'),
                    ('Bob Johnson', '+491234567890', 'bob@demo.com', 'Demo Ltd')"
            ];
            
            foreach ($sampleData as $sql) {
                $this->pdo->exec($sql);
            }
        }
    }
    
    public function getPDO() {
        return $this->pdo;
    }
    
    public function getAllScripts() {
        $stmt = $this->pdo->query("SELECT * FROM scripts ORDER BY created_at DESC");
        return $stmt->fetchAll();
    }
    
    public function getAllFAQs() {
        $stmt = $this->pdo->query("SELECT * FROM faqs ORDER BY created_at DESC");
        return $stmt->fetchAll();
    }
    
    public function getAllCustomers() {
        $stmt = $this->pdo->query("SELECT * FROM customers ORDER BY created_at DESC");
        return $stmt->fetchAll();
    }
    
    public function getAllCalls() {
        $stmt = $this->pdo->query("
            SELECT c.*, cu.name as customer_name, cu.company 
            FROM calls c 
            LEFT JOIN customers cu ON c.customer_id = cu.id 
            ORDER BY c.start_time DESC 
            LIMIT 100
        ");
        return $stmt->fetchAll();
    }
    
    public function getCallStats() {
        $today = date('Y-m-d');
        
        $stats = [
            'active_calls' => 0,
            'total_calls_today' => 0,
            'success_rate' => 0,
            'leads_generated' => 0
        ];
        
        // Total calls today
        $stmt = $this->pdo->prepare("SELECT COUNT(*) FROM calls WHERE DATE(start_time) = ?");
        $stmt->execute([$today]);
        $stats['total_calls_today'] = $stmt->fetchColumn();
        
        // Success rate (calls longer than 2 minutes)
        if ($stats['total_calls_today'] > 0) {
            $stmt = $this->pdo->prepare("SELECT COUNT(*) FROM calls WHERE DATE(start_time) = ? AND duration > 120");
            $stmt->execute([$today]);
            $successful = $stmt->fetchColumn();
            $stats['success_rate'] = round(($successful / $stats['total_calls_today']) * 100, 1);
        }
        
        // Leads generated (successful calls with notes)
        $stmt = $this->pdo->prepare("SELECT COUNT(*) FROM calls WHERE DATE(start_time) = ? AND duration > 120 AND notes IS NOT NULL AND notes != ''");
        $stmt->execute([$today]);
        $stats['leads_generated'] = $stmt->fetchColumn();
        
        return $stats;
    }
    
    public function addScript($name, $context, $content) {
        $stmt = $this->pdo->prepare("INSERT INTO scripts (name, context, content) VALUES (?, ?, ?)");
        return $stmt->execute([$name, $context, $content]);
    }
    
    public function updateScript($id, $name, $context, $content) {
        $stmt = $this->pdo->prepare("UPDATE scripts SET name = ?, context = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        return $stmt->execute([$name, $context, $content, $id]);
    }
    
    public function deleteScript($id) {
        $stmt = $this->pdo->prepare("DELETE FROM scripts WHERE id = ?");
        return $stmt->execute([$id]);
    }
    
    public function addFAQ($question, $answer, $category) {
        $stmt = $this->pdo->prepare("INSERT INTO faqs (question, answer, category) VALUES (?, ?, ?)");
        return $stmt->execute([$question, $answer, $category]);
    }
    
    public function updateFAQ($id, $question, $answer, $category) {
        $stmt = $this->pdo->prepare("UPDATE faqs SET question = ?, answer = ?, category = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        return $stmt->execute([$question, $answer, $category, $id]);
    }
    
    public function deleteFAQ($id) {
        $stmt = $this->pdo->prepare("DELETE FROM faqs WHERE id = ?");
        return $stmt->execute([$id]);
    }
    
    public function addCustomer($name, $phone, $email, $company, $notes) {
        $stmt = $this->pdo->prepare("INSERT INTO customers (name, phone, email, company, notes) VALUES (?, ?, ?, ?, ?)");
        return $stmt->execute([$name, $phone, $email, $company, $notes]);
    }
    
    public function updateCustomer($id, $name, $phone, $email, $company, $notes) {
        $stmt = $this->pdo->prepare("UPDATE customers SET name = ?, phone = ?, email = ?, company = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?");
        return $stmt->execute([$name, $phone, $email, $company, $notes, $id]);
    }
    
    public function deleteCustomer($id) {
        $stmt = $this->pdo->prepare("DELETE FROM customers WHERE id = ?");
        return $stmt->execute([$id]);
    }
}