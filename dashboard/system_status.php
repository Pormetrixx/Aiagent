<?php
require_once 'db.php';

session_start();

// Check authentication
if (!isset($_SESSION['logged_in'])) {
    header('HTTP/1.1 403 Forbidden');
    exit('Access denied');
}

// Check system status
function checkSystemStatus() {
    $status = [
        'ai_agent' => false,
        'asterisk' => false,
        'database' => false
    ];
    
    // Check AI Agent (look for running process)
    $output = shell_exec('pgrep -f "python.*run.py start" 2>/dev/null');
    $status['ai_agent'] = !empty(trim($output));
    
    // Check Asterisk
    $output = shell_exec('systemctl is-active asterisk 2>/dev/null');
    $status['asterisk'] = trim($output) === 'active';
    
    // Check database connection
    try {
        $db = new DatabaseHelper();
        $status['database'] = true;
    } catch (Exception $e) {
        $status['database'] = false;
    }
    
    return $status;
}

function getCallStats() {
    try {
        $db = new DatabaseHelper();
        return $db->getCallStats();
    } catch (Exception $e) {
        return [
            'active_calls' => 0,
            'total_calls_today' => 0,
            'success_rate' => 0,
            'leads_generated' => 0
        ];
    }
}

// Handle AJAX requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    switch ($action) {
        case 'get_status':
            $status = checkSystemStatus();
            $stats = getCallStats();
            echo json_encode([
                'success' => true,
                'status' => $status,
                'stats' => $stats
            ]);
            break;
            
        case 'start_agent':
            // In a real implementation, this would start the AI agent
            $output = shell_exec('sudo systemctl start aiagent 2>&1');
            sleep(2); // Give it time to start
            $status = checkSystemStatus();
            echo json_encode([
                'success' => $status['ai_agent'],
                'message' => $status['ai_agent'] ? 'AI Agent started successfully' : 'Failed to start AI Agent',
                'output' => $output
            ]);
            break;
            
        case 'stop_agent':
            $output = shell_exec('sudo systemctl stop aiagent 2>&1');
            sleep(1);
            $status = checkSystemStatus();
            echo json_encode([
                'success' => !$status['ai_agent'],
                'message' => !$status['ai_agent'] ? 'AI Agent stopped successfully' : 'Failed to stop AI Agent',
                'output' => $output
            ]);
            break;
            
        case 'restart_asterisk':
            $output = shell_exec('sudo systemctl restart asterisk 2>&1');
            sleep(3);
            $status = checkSystemStatus();
            echo json_encode([
                'success' => $status['asterisk'],
                'message' => $status['asterisk'] ? 'Asterisk restarted successfully' : 'Failed to restart Asterisk',
                'output' => $output
            ]);
            break;
            
        default:
            echo json_encode(['success' => false, 'error' => 'Invalid action']);
    }
    exit;
}

// Return status for GET requests
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $status = checkSystemStatus();
    $stats = getCallStats();
    
    echo json_encode([
        'success' => true,
        'status' => $status,
        'stats' => $stats,
        'timestamp' => time()
    ]);
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>