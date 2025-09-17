<?php
require_once 'db.php';

session_start();

// Check authentication
if (!isset($_SESSION['logged_in'])) {
    header('HTTP/1.1 403 Forbidden');
    exit('Access denied');
}

// Configuration file path
$config_file = '/home/' . get_current_user() . '/aiagent/config/config.yaml';

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    try {
        switch ($action) {
            case 'save_settings':
                $settings = [
                    'database' => [
                        'host' => $_POST['db_host'] ?? 'localhost',
                        'name' => $_POST['db_name'] ?? 'aiagent',
                        'user' => $_POST['db_user'] ?? 'aiagent_user',
                        'password' => $_POST['db_password'] ?? ''
                    ],
                    'asterisk' => [
                        'host' => $_POST['asterisk_host'] ?? 'localhost',
                        'port' => (int)($_POST['asterisk_port'] ?? 5038),
                        'username' => $_POST['asterisk_user'] ?? 'admin',
                        'password' => $_POST['asterisk_password'] ?? '',
                        'caller_id' => $_POST['caller_id'] ?? 'AI Agent <1000>'
                    ],
                    'call_settings' => [
                        'max_duration' => (int)($_POST['max_duration'] ?? 15),
                        'retry_attempts' => (int)($_POST['retry_attempts'] ?? 3),
                        'recording_enabled' => isset($_POST['recording_enabled'])
                    ]
                ];
                
                // Save to YAML file (simplified version)
                $yaml_content = generateYAMLContent($settings);
                
                if (file_exists($config_file) && is_writable($config_file)) {
                    file_put_contents($config_file, $yaml_content);
                    echo json_encode(['success' => true, 'message' => 'Settings saved successfully']);
                } else {
                    throw new Exception('Configuration file not writable: ' . $config_file);
                }
                break;
                
            case 'get_settings':
                if (file_exists($config_file)) {
                    $settings = parseYAMLFile($config_file);
                    echo json_encode(['success' => true, 'settings' => $settings]);
                } else {
                    // Return default settings
                    $settings = [
                        'database' => [
                            'host' => 'localhost',
                            'name' => 'aiagent',
                            'user' => 'aiagent_user',
                            'password' => ''
                        ],
                        'asterisk' => [
                            'host' => 'localhost',
                            'port' => 5038,
                            'username' => 'admin',
                            'password' => '',
                            'caller_id' => 'AI Agent <1000>'
                        ],
                        'call_settings' => [
                            'max_duration' => 15,
                            'retry_attempts' => 3,
                            'recording_enabled' => true
                        ]
                    ];
                    echo json_encode(['success' => true, 'settings' => $settings]);
                }
                break;
                
            case 'test_database':
                $host = $_POST['db_host'] ?? 'localhost';
                $name = $_POST['db_name'] ?? 'aiagent';
                $user = $_POST['db_user'] ?? 'aiagent_user';
                $password = $_POST['db_password'] ?? '';
                
                try {
                    $dsn = "mysql:host=$host;dbname=$name;charset=utf8mb4";
                    $pdo = new PDO($dsn, $user, $password);
                    echo json_encode(['success' => true, 'message' => 'Database connection successful']);
                } catch (PDOException $e) {
                    throw new Exception('Database connection failed: ' . $e->getMessage());
                }
                break;
                
            case 'test_asterisk':
                $host = $_POST['asterisk_host'] ?? 'localhost';
                $port = (int)($_POST['asterisk_port'] ?? 5038);
                
                $socket = @fsockopen($host, $port, $errno, $errstr, 5);
                if ($socket) {
                    fclose($socket);
                    echo json_encode(['success' => true, 'message' => 'Asterisk connection successful']);
                } else {
                    throw new Exception("Asterisk connection failed: $errstr ($errno)");
                }
                break;
                
            default:
                throw new Exception('Invalid action');
        }
        
    } catch (Exception $e) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
    
    exit;
}

function generateYAMLContent($settings) {
    $yaml = "# AI Cold Calling Agent Configuration\n";
    $yaml .= "# Generated by web dashboard on " . date('Y-m-d H:i:s') . "\n\n";
    
    $yaml .= "database:\n";
    $yaml .= "  type: mysql\n";
    $yaml .= "  host: " . $settings['database']['host'] . "\n";
    $yaml .= "  port: 3306\n";
    $yaml .= "  name: " . $settings['database']['name'] . "\n";
    $yaml .= "  username: " . $settings['database']['user'] . "\n";
    $yaml .= "  password: " . $settings['database']['password'] . "\n\n";
    
    $yaml .= "asterisk:\n";
    $yaml .= "  enabled: true\n";
    $yaml .= "  host: " . $settings['asterisk']['host'] . "\n";
    $yaml .= "  port: " . $settings['asterisk']['port'] . "\n";
    $yaml .= "  username: " . $settings['asterisk']['username'] . "\n";
    $yaml .= "  password: " . $settings['asterisk']['password'] . "\n";
    $yaml .= "  channel_technology: SIP\n";
    $yaml .= "  context: outbound\n";
    $yaml .= "  caller_id: \"" . $settings['asterisk']['caller_id'] . "\"\n\n";
    
    $yaml .= "call_settings:\n";
    $yaml .= "  max_call_duration_minutes: " . $settings['call_settings']['max_duration'] . "\n";
    $yaml .= "  retry_attempts: " . $settings['call_settings']['retry_attempts'] . "\n";
    $yaml .= "  recording_enabled: " . ($settings['call_settings']['recording_enabled'] ? 'true' : 'false') . "\n";
    
    return $yaml;
}

function parseYAMLFile($file) {
    // Simple YAML parser for basic key-value pairs
    $content = file_get_contents($file);
    $lines = explode("\n", $content);
    $settings = [];
    $current_section = null;
    
    foreach ($lines as $line) {
        $line = trim($line);
        if (empty($line) || strpos($line, '#') === 0) continue;
        
        if (preg_match('/^(\w+):$/', $line, $matches)) {
            $current_section = $matches[1];
            $settings[$current_section] = [];
        } elseif (preg_match('/^\s*(\w+):\s*(.+)$/', $line, $matches)) {
            $key = $matches[1];
            $value = trim($matches[2], '"\'');
            
            if ($current_section) {
                $settings[$current_section][$key] = $value;
            } else {
                $settings[$key] = $value;
            }
        }
    }
    
    return $settings;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>