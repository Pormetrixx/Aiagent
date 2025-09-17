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
                $question = trim($_POST['question'] ?? '');
                $answer = trim($_POST['answer'] ?? '');
                $category = $_POST['category'] ?? 'general';
                
                if (empty($question) || empty($answer)) {
                    throw new Exception('Question and answer are required');
                }
                
                $db->addFAQ($question, $answer, $category);
                echo json_encode(['success' => true, 'message' => 'FAQ added successfully']);
                break;
                
            case 'edit':
                $id = (int)($_POST['id'] ?? 0);
                $question = trim($_POST['question'] ?? '');
                $answer = trim($_POST['answer'] ?? '');
                $category = $_POST['category'] ?? 'general';
                
                if (empty($question) || empty($answer) || $id <= 0) {
                    throw new Exception('Invalid data provided');
                }
                
                $db->updateFAQ($id, $question, $answer, $category);
                echo json_encode(['success' => true, 'message' => 'FAQ updated successfully']);
                break;
                
            case 'delete':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid FAQ ID');
                }
                
                $db->deleteFAQ($id);
                echo json_encode(['success' => true, 'message' => 'FAQ deleted successfully']);
                break;
                
            case 'get':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid FAQ ID');
                }
                
                $stmt = $db->getPDO()->prepare("SELECT * FROM faqs WHERE id = ?");
                $stmt->execute([$id]);
                $faq = $stmt->fetch();
                
                if (!$faq) {
                    throw new Exception('FAQ not found');
                }
                
                echo json_encode(['success' => true, 'faq' => $faq]);
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

// Return list of FAQs for GET requests
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        $faqs = $db->getAllFAQs();
        echo json_encode(['success' => true, 'faqs' => $faqs]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>