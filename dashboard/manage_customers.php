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
                $name = trim($_POST['name'] ?? '');
                $phone = trim($_POST['phone'] ?? '');
                $email = trim($_POST['email'] ?? '');
                $company = trim($_POST['company'] ?? '');
                $notes = trim($_POST['notes'] ?? '');
                
                if (empty($name) || empty($phone)) {
                    throw new Exception('Name and phone are required');
                }
                
                // Validate phone format
                if (!preg_match('/^\+?[1-9]\d{1,14}$/', str_replace([' ', '-', '(', ')'], '', $phone))) {
                    throw new Exception('Invalid phone number format');
                }
                
                $db->addCustomer($name, $phone, $email, $company, $notes);
                echo json_encode(['success' => true, 'message' => 'Customer added successfully']);
                break;
                
            case 'edit':
                $id = (int)($_POST['id'] ?? 0);
                $name = trim($_POST['name'] ?? '');
                $phone = trim($_POST['phone'] ?? '');
                $email = trim($_POST['email'] ?? '');
                $company = trim($_POST['company'] ?? '');
                $notes = trim($_POST['notes'] ?? '');
                
                if (empty($name) || empty($phone) || $id <= 0) {
                    throw new Exception('Invalid data provided');
                }
                
                // Validate phone format
                if (!preg_match('/^\+?[1-9]\d{1,14}$/', str_replace([' ', '-', '(', ')'], '', $phone))) {
                    throw new Exception('Invalid phone number format');
                }
                
                $db->updateCustomer($id, $name, $phone, $email, $company, $notes);
                echo json_encode(['success' => true, 'message' => 'Customer updated successfully']);
                break;
                
            case 'delete':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid customer ID');
                }
                
                $db->deleteCustomer($id);
                echo json_encode(['success' => true, 'message' => 'Customer deleted successfully']);
                break;
                
            case 'get':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid customer ID');
                }
                
                $stmt = $db->getPDO()->prepare("SELECT * FROM customers WHERE id = ?");
                $stmt->execute([$id]);
                $customer = $stmt->fetch();
                
                if (!$customer) {
                    throw new Exception('Customer not found');
                }
                
                echo json_encode(['success' => true, 'customer' => $customer]);
                break;
                
            case 'call':
                $id = (int)($_POST['id'] ?? 0);
                
                if ($id <= 0) {
                    throw new Exception('Invalid customer ID');
                }
                
                $stmt = $db->getPDO()->prepare("SELECT * FROM customers WHERE id = ?");
                $stmt->execute([$id]);
                $customer = $stmt->fetch();
                
                if (!$customer) {
                    throw new Exception('Customer not found');
                }
                
                // In a real implementation, this would trigger the AI agent to make a call
                // For now, we'll just log the call attempt
                $stmt = $db->getPDO()->prepare("INSERT INTO calls (customer_id, phone, status, notes) VALUES (?, ?, 'initiated', 'Call initiated from dashboard')");
                $stmt->execute([$id, $customer['phone']]);
                
                echo json_encode(['success' => true, 'message' => 'Call initiated for ' . $customer['name']]);
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

// Return list of customers for GET requests
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    try {
        $customers = $db->getAllCustomers();
        echo json_encode(['success' => true, 'customers' => $customers]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    }
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>