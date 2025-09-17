<?php
require_once 'db.php';

session_start();

// Check authentication
if (!isset($_SESSION['logged_in'])) {
    header('HTTP/1.1 403 Forbidden');
    exit('Access denied');
}

$db = new DatabaseHelper();

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    try {
        switch ($action) {
            case 'add':
                $name = trim($_POST['script_name'] ?? '');
                $context = $_POST['context'] ?? '';
                $content = trim($_POST['content'] ?? '');
                
                if (empty($name) || empty($content)) {
                    throw new Exception('Name and content are required');
                }
                
                $db->addScript($name, $context, $content);
                echo json_encode(['success' => true, 'message' => 'Script added successfully']);
                break;
                
            case 'edit':
                $id = (int)($_POST['id'] ?? 0);
                $name = trim($_POST['script_name'] ?? '');
                $context = $_POST['context'] ?? '';
                $content = trim($_POST['content'] ?? '');
                
                if (empty($name) || empty($content) || $id <= 0) {
                    throw new Exception('Invalid data provided');
                }
                
                $db->updateScript($id, $name, $context, $content);
                echo json_encode(['success' => true, 'message' => 'Script updated successfully']);
                break;
                
            case 'delete':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid script ID');
                }
                
                $db->deleteScript($id);
                echo json_encode(['success' => true, 'message' => 'Script deleted successfully']);
                break;
                
            case 'get':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid script ID');
                }
                
                $stmt = $db->getPDO()->prepare("SELECT * FROM scripts WHERE id = ?");
                $stmt->execute([$id]);
                $script = $stmt->fetch();
                
                if (!$script) {
                    throw new Exception('Script not found');
                }
                
                echo json_encode(['success' => true, 'script' => $script]);
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

// Return list of scripts for GET requests
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        $scripts = $db->getAllScripts();
        echo json_encode(['success' => true, 'scripts' => $scripts]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>