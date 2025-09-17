<?php
session_start();
require_once 'dashboard/db.php';

// Simple authentication
$valid_users = ['admin' => 'admin123'];

if ($_POST['action'] === 'login') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if (isset($valid_users[$username]) && $valid_users[$username] === $password) {
        $_SESSION['logged_in'] = true;
        $_SESSION['username'] = $username;
    } else {
        $login_error = 'Invalid credentials';
    }
}

if ($_POST['action'] === 'logout') {
    session_destroy();
    header('Location: index.php');
    exit;
}

if (!isset($_SESSION['logged_in'])) {
    include 'dashboard_login.php';
    exit;
}

// Initialize database
try {
    $db = new DatabaseHelper();
    $stats = $db->getCallStats();
} catch (Exception $e) {
    $stats = ['active_calls' => 0, 'total_calls_today' => 0, 'success_rate' => 0, 'leads_generated' => 0];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cold Calling Agent - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { font-size: 1.5rem; }
        .nav { background: #2c3e50; padding: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-menu { list-style: none; display: flex; margin: 0; }
        .nav-menu li { border-right: 1px solid #34495e; }
        .nav-menu a { color: white; text-decoration: none; padding: 1rem 1.5rem; display: block; transition: background 0.3s; }
        .nav-menu a:hover, .nav-menu a.active { background: #34495e; }
        .container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
        .card { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #e1e8ed; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .btn { background: #3498db; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; transition: all 0.3s; font-size: 0.9rem; }
        .btn:hover { background: #2980b9; transform: translateY(-1px); }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .btn-small { padding: 0.4rem 0.8rem; font-size: 0.8rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.75rem; border: 2px solid #e1e8ed; border-radius: 6px; font-size: 0.9rem; transition: border-color 0.3s; }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #3498db; }
        .form-group textarea { height: 120px; resize: vertical; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 0.5rem; }
        .status-online { background: #27ae60; }
        .status-offline { background: #e74c3c; }
        .status-warning { background: #f39c12; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; position: relative; overflow: hidden; }
        .stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%); }
        .stat-number { font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e1e8ed; }
        .table th { background: #f8f9fa; font-weight: 600; color: #2c3e50; }
        .table tr:hover { background: #f8f9fa; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 2rem; border-radius: 8px; width: 90%; max-width: 600px; position: relative; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .loading { display: none; text-align: center; padding: 2rem; }
        .loading::after { content: ''; display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .alert { padding: 1rem; margin: 1rem 0; border-radius: 6px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Cold Calling Agent Dashboard</h1>
        <div>
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?></span>
            <form method="post" style="display: inline; margin-left: 1rem;">
                <input type="hidden" name="action" value="logout">
                <button type="submit" class="btn btn-danger btn-small">Logout</button>
            </form>
        </div>
    </div>
    
    <nav class="nav">
        <ul class="nav-menu">
            <li><a href="#" onclick="showSection('dashboard')" class="active">📊 Dashboard</a></li>
            <li><a href="#" onclick="showSection('scripts')">📝 Scripts</a></li>
            <li><a href="#" onclick="showSection('faqs')">❓ FAQs</a></li>
            <li><a href="#" onclick="showSection('customers')">👥 Customers</a></li>
            <li><a href="#" onclick="showSection('calls')">📞 Calls</a></li>
            <li><a href="#" onclick="showSection('settings')">⚙️ Settings</a></li>
        </ul>
    </nav>
    
    <div class="container">
        <!-- Dashboard Section -->
        <div id="dashboard" class="section">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="active-calls"><?php echo $stats['active_calls']; ?></div>
                    <div class="stat-label">Active Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="total-calls"><?php echo $stats['total_calls_today']; ?></div>
                    <div class="stat-label">Total Calls Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="success-rate"><?php echo $stats['success_rate']; ?>%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="leads-generated"><?php echo $stats['leads_generated']; ?></div>
                    <div class="stat-label">Leads Generated</div>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>🔧 System Status</h3>
                    <div id="system-status">
                        <p><span class="status-indicator status-offline" id="ai-status"></span>AI Agent: <span id="ai-text">Checking...</span></p>
                        <p><span class="status-indicator status-offline" id="asterisk-status"></span>Asterisk PBX: <span id="asterisk-text">Checking...</span></p>
                        <p><span class="status-indicator status-offline" id="db-status"></span>Database: <span id="db-text">Checking...</span></p>
                    </div>
                    <div style="margin-top: 1rem;">
                        <button class="btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                        <button class="btn btn-success" onclick="startAgent()">▶️ Start Agent</button>
                        <button class="btn btn-danger" onclick="stopAgent()">⏹️ Stop Agent</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ Quick Actions</h3>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <button class="btn" onclick="showSection('calls')">📞 View Call Logs</button>
                        <button class="btn" onclick="showSection('customers')">👥 Manage Customers</button>
                        <button class="btn" onclick="showSection('scripts')">📝 Edit Scripts</button>
                        <button class="btn" onclick="showSection('faqs')">❓ Update FAQs</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Scripts Section -->
        <div id="scripts" class="section hidden">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>📝 Conversation Scripts</h3>
                    <button class="btn" onclick="showScriptForm()">➕ Add New Script</button>
                </div>
                
                <div id="scripts-table-container">
                    <div class="loading" id="scripts-loading">Loading scripts...</div>
                    <table class="table" id="scripts-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Context</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="scripts-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- FAQs Section -->
        <div id="faqs" class="section hidden">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>❓ Frequently Asked Questions</h3>
                    <button class="btn" onclick="showFAQForm()">➕ Add New FAQ</button>
                </div>
                
                <div id="faqs-table-container">
                    <div class="loading" id="faqs-loading">Loading FAQs...</div>
                    <table class="table" id="faqs-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>Question</th>
                                <th>Category</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="faqs-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Customers Section -->
        <div id="customers" class="section hidden">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3>👥 Customer Management</h3>
                    <button class="btn" onclick="showCustomerForm()">➕ Add New Customer</button>
                </div>
                
                <div id="customers-table-container">
                    <div class="loading" id="customers-loading">Loading customers...</div>
                    <table class="table" id="customers-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Phone</th>
                                <th>Company</th>
                                <th>Last Contact</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="customers-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Calls Section -->
        <div id="calls" class="section hidden">
            <div class="card">
                <h3>📞 Call History</h3>
                <div id="calls-table-container">
                    <div class="loading" id="calls-loading">Loading call history...</div>
                    <table class="table" id="calls-table" style="display: none;">
                        <thead>
                            <tr>
                                <th>Date/Time</th>
                                <th>Customer</th>
                                <th>Phone</th>
                                <th>Duration</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="calls-tbody">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Settings Section -->
        <div id="settings" class="section hidden">
            <div class="card">
                <h3>⚙️ System Settings</h3>
                <div id="settings-form-container">
                    <div class="loading" id="settings-loading">Loading settings...</div>
                    <form id="settings-form" style="display: none;">
                        <h4>🗃️ Database Configuration</h4>
                        <div class="grid" style="grid-template-columns: 1fr 1fr;">
                            <div class="form-group">
                                <label>Database Host</label>
                                <input type="text" name="db_host" value="localhost">
                            </div>
                            <div class="form-group">
                                <label>Database Name</label>
                                <input type="text" name="db_name" value="aiagent">
                            </div>
                            <div class="form-group">
                                <label>Database User</label>
                                <input type="text" name="db_user" value="aiagent_user">
                            </div>
                            <div class="form-group">
                                <label>Database Password</label>
                                <input type="password" name="db_password">
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 2rem;">📞 Asterisk Configuration</h4>
                        <div class="grid" style="grid-template-columns: 1fr 1fr;">
                            <div class="form-group">
                                <label>Asterisk Host</label>
                                <input type="text" name="asterisk_host" value="localhost">
                            </div>
                            <div class="form-group">
                                <label>AMI Port</label>
                                <input type="number" name="asterisk_port" value="5038">
                            </div>
                            <div class="form-group">
                                <label>AMI Username</label>
                                <input type="text" name="asterisk_user" value="admin">
                            </div>
                            <div class="form-group">
                                <label>AMI Password</label>
                                <input type="password" name="asterisk_password">
                            </div>
                        </div>
                        
                        <h4 style="margin-top: 2rem;">⚙️ Call Settings</h4>
                        <div class="grid" style="grid-template-columns: 1fr 1fr 1fr;">
                            <div class="form-group">
                                <label>Max Duration (minutes)</label>
                                <input type="number" name="max_duration" value="15">
                            </div>
                            <div class="form-group">
                                <label>Retry Attempts</label>
                                <input type="number" name="retry_attempts" value="3">
                            </div>
                            <div class="form-group">
                                <label>Default Caller ID</label>
                                <input type="text" name="caller_id" value="AI Agent <1000>">
                            </div>
                        </div>
                        
                        <div style="margin-top: 2rem;">
                            <button type="button" class="btn" onclick="testDatabase()">🧪 Test Database</button>
                            <button type="button" class="btn" onclick="testAsterisk()">🧪 Test Asterisk</button>
                            <button type="submit" class="btn btn-success">💾 Save Settings</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal for forms -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modal-body">
            </div>
        </div>
    </div>
    
    <!-- Alert container -->
    <div id="alert-container" style="position: fixed; top: 20px; right: 20px; z-index: 1100;"></div>
    
    <script>
        // Global variables
        let currentSection = 'dashboard';
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshStatus();
            loadData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshStatus, 30000);
        });
        
        // Navigation functions
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => section.classList.add('hidden'));
            
            // Show selected section
            document.getElementById(sectionId).classList.remove('hidden');
            
            // Update navigation
            const navLinks = document.querySelectorAll('.nav-menu a');
            navLinks.forEach(link => link.classList.remove('active'));
            event.target.classList.add('active');
            
            currentSection = sectionId;
            
            // Load data for the section
            loadSectionData(sectionId);
        }
        
        function loadSectionData(sectionId) {
            switch(sectionId) {
                case 'scripts':
                    loadScripts();
                    break;
                case 'faqs':
                    loadFAQs();
                    break;
                case 'customers':
                    loadCustomers();
                    break;
                case 'calls':
                    loadCalls();
                    break;
                case 'settings':
                    loadSettings();
                    break;
            }
        }
        
        function loadData() {
            loadScripts();
            loadFAQs();
            loadCustomers();
            loadCalls();
        }
        
        // System status functions
        function refreshStatus() {
            fetch('dashboard/system_status.php')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateSystemStatus(data.status);
                        updateStats(data.stats);
                    }
                })
                .catch(error => console.error('Error refreshing status:', error));
        }
        
        function updateSystemStatus(status) {
            // Update AI Agent status
            const aiIndicator = document.getElementById('ai-status');
            const aiText = document.getElementById('ai-text');
            if (status.ai_agent) {
                aiIndicator.className = 'status-indicator status-online';
                aiText.textContent = 'Online';
            } else {
                aiIndicator.className = 'status-indicator status-offline';
                aiText.textContent = 'Offline';
            }
            
            // Update Asterisk status
            const asteriskIndicator = document.getElementById('asterisk-status');
            const asteriskText = document.getElementById('asterisk-text');
            if (status.asterisk) {
                asteriskIndicator.className = 'status-indicator status-online';
                asteriskText.textContent = 'Online';
            } else {
                asteriskIndicator.className = 'status-indicator status-offline';
                asteriskText.textContent = 'Offline';
            }
            
            // Update Database status
            const dbIndicator = document.getElementById('db-status');
            const dbText = document.getElementById('db-text');
            if (status.database) {
                dbIndicator.className = 'status-indicator status-online';
                dbText.textContent = 'Connected';
            } else {
                dbIndicator.className = 'status-indicator status-offline';
                dbText.textContent = 'Disconnected';
            }
        }
        
        function updateStats(stats) {
            document.getElementById('active-calls').textContent = stats.active_calls;
            document.getElementById('total-calls').textContent = stats.total_calls_today;
            document.getElementById('success-rate').textContent = stats.success_rate + '%';
            document.getElementById('leads-generated').textContent = stats.leads_generated;
        }
        
        function startAgent() {
            showAlert('Starting AI Agent...', 'info');
            
            fetch('dashboard/system_status.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=start_agent'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('AI Agent started successfully', 'success');
                } else {
                    showAlert('Failed to start AI Agent: ' + data.message, 'error');
                }
                refreshStatus();
            })
            .catch(error => {
                showAlert('Error starting AI Agent: ' + error.message, 'error');
            });
        }
        
        function stopAgent() {
            showAlert('Stopping AI Agent...', 'info');
            
            fetch('dashboard/system_status.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=stop_agent'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('AI Agent stopped successfully', 'success');
                } else {
                    showAlert('Failed to stop AI Agent: ' + data.message, 'error');
                }
                refreshStatus();
            })
            .catch(error => {
                showAlert('Error stopping AI Agent: ' + error.message, 'error');
            });
        }
        
        // Scripts functions
        function loadScripts() {
            const loading = document.getElementById('scripts-loading');
            const table = document.getElementById('scripts-table');
            const tbody = document.getElementById('scripts-tbody');
            
            loading.style.display = 'block';
            table.style.display = 'none';
            
            fetch('dashboard/manage_scripts.php')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        tbody.innerHTML = '';
                        data.scripts.forEach(script => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${escapeHtml(script.name)}</td>
                                <td><span class="badge">${escapeHtml(script.context)}</span></td>
                                <td>${new Date(script.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-small" onclick="editScript(${script.id})">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="deleteScript(${script.id})">Delete</button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                        table.style.display = 'table';
                    } else {
                        showAlert('Error loading scripts: ' + data.error, 'error');
                    }
                    loading.style.display = 'none';
                })
                .catch(error => {
                    showAlert('Error loading scripts: ' + error.message, 'error');
                    loading.style.display = 'none';
                });
        }
        
        function showScriptForm(script = null) {
            const isEdit = script !== null;
            const modalBody = document.getElementById('modal-body');
            
            modalBody.innerHTML = `
                <h3>${isEdit ? 'Edit Script' : 'Add New Script'}</h3>
                <form id="script-form">
                    <input type="hidden" name="action" value="${isEdit ? 'edit' : 'add'}">
                    ${isEdit ? `<input type="hidden" name="id" value="${script.id}">` : ''}
                    
                    <div class="form-group">
                        <label>Script Name</label>
                        <input type="text" name="script_name" value="${isEdit ? escapeHtml(script.name) : ''}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Context</label>
                        <select name="context" required>
                            <option value="opening" ${isEdit && script.context === 'opening' ? 'selected' : ''}>Opening</option>
                            <option value="questioning" ${isEdit && script.context === 'questioning' ? 'selected' : ''}>Questioning</option>
                            <option value="presenting" ${isEdit && script.context === 'presenting' ? 'selected' : ''}>Presenting</option>
                            <option value="objection_handling" ${isEdit && script.context === 'objection_handling' ? 'selected' : ''}>Objection Handling</option>
                            <option value="closing" ${isEdit && script.context === 'closing' ? 'selected' : ''}>Closing</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Script Content</label>
                        <textarea name="content" placeholder="Enter the script content here..." required>${isEdit ? escapeHtml(script.content) : ''}</textarea>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <button type="submit" class="btn btn-success">💾 Save Script</button>
                        <button type="button" class="btn btn-danger" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            `;
            
            document.getElementById('modal').style.display = 'block';
            
            // Add form submit handler
            document.getElementById('script-form').addEventListener('submit', function(e) {
                e.preventDefault();
                saveScript(new FormData(this));
            });
        }
        
        function editScript(id) {
            fetch('dashboard/manage_scripts.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=get&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showScriptForm(data.script);
                } else {
                    showAlert('Error loading script: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showAlert('Error loading script: ' + error.message, 'error');
            });
        }
        
        function saveScript(formData) {
            fetch('dashboard/manage_scripts.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    closeModal();
                    loadScripts();
                } else {
                    showAlert('Error saving script: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showAlert('Error saving script: ' + error.message, 'error');
            });
        }
        
        function deleteScript(id) {
            if (!confirm('Are you sure you want to delete this script?')) return;
            
            fetch('dashboard/manage_scripts.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=delete&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadScripts();
                } else {
                    showAlert('Error deleting script: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showAlert('Error deleting script: ' + error.message, 'error');
            });
        }
        
        // FAQ functions (similar pattern to scripts)
        function loadFAQs() {
            const loading = document.getElementById('faqs-loading');
            const table = document.getElementById('faqs-table');
            const tbody = document.getElementById('faqs-tbody');
            
            loading.style.display = 'block';
            table.style.display = 'none';
            
            fetch('dashboard/manage_faqs.php')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        tbody.innerHTML = '';
                        data.faqs.forEach(faq => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${escapeHtml(faq.question.substring(0, 50))}${faq.question.length > 50 ? '...' : ''}</td>
                                <td><span class="badge">${escapeHtml(faq.category)}</span></td>
                                <td>${new Date(faq.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-small" onclick="editFAQ(${faq.id})">Edit</button>
                                    <button class="btn btn-danger btn-small" onclick="deleteFAQ(${faq.id})">Delete</button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                        table.style.display = 'table';
                    } else {
                        showAlert('Error loading FAQs: ' + data.error, 'error');
                    }
                    loading.style.display = 'none';
                })
                .catch(error => {
                    showAlert('Error loading FAQs: ' + error.message, 'error');
                    loading.style.display = 'none';
                });
        }
        
        function showFAQForm(faq = null) {
            const isEdit = faq !== null;
            const modalBody = document.getElementById('modal-body');
            
            modalBody.innerHTML = `
                <h3>${isEdit ? 'Edit FAQ' : 'Add New FAQ'}</h3>
                <form id="faq-form">
                    <input type="hidden" name="action" value="${isEdit ? 'edit' : 'add'}">
                    ${isEdit ? `<input type="hidden" name="id" value="${faq.id}">` : ''}
                    
                    <div class="form-group">
                        <label>Question</label>
                        <input type="text" name="question" value="${isEdit ? escapeHtml(faq.question) : ''}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Answer</label>
                        <textarea name="answer" placeholder="Enter the answer here..." required>${isEdit ? escapeHtml(faq.answer) : ''}</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Category</label>
                        <select name="category" required>
                            <option value="general" ${isEdit && faq.category === 'general' ? 'selected' : ''}>General</option>
                            <option value="pricing" ${isEdit && faq.category === 'pricing' ? 'selected' : ''}>Pricing</option>
                            <option value="technical" ${isEdit && faq.category === 'technical' ? 'selected' : ''}>Technical</option>
                            <option value="support" ${isEdit && faq.category === 'support' ? 'selected' : ''}>Support</option>
                        </select>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <button type="submit" class="btn btn-success">💾 Save FAQ</button>
                        <button type="button" class="btn btn-danger" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            `;
            
            document.getElementById('modal').style.display = 'block';
            
            // Add form submit handler
            document.getElementById('faq-form').addEventListener('submit', function(e) {
                e.preventDefault();
                saveFAQ(new FormData(this));
            });
        }
        
        function editFAQ(id) {
            fetch('dashboard/manage_faqs.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=get&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showFAQForm(data.faq);
                } else {
                    showAlert('Error loading FAQ: ' + data.error, 'error');
                }
            });
        }
        
        function saveFAQ(formData) {
            fetch('dashboard/manage_faqs.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    closeModal();
                    loadFAQs();
                } else {
                    showAlert('Error saving FAQ: ' + data.error, 'error');
                }
            });
        }
        
        function deleteFAQ(id) {
            if (!confirm('Are you sure you want to delete this FAQ?')) return;
            
            fetch('dashboard/manage_faqs.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=delete&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadFAQs();
                } else {
                    showAlert('Error deleting FAQ: ' + data.error, 'error');
                }
            });
        }
        
        // Customer functions (similar pattern)
        function loadCustomers() {
            const loading = document.getElementById('customers-loading');
            const table = document.getElementById('customers-table');
            const tbody = document.getElementById('customers-tbody');
            
            loading.style.display = 'block';
            table.style.display = 'none';
            
            fetch('dashboard/manage_customers.php')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        tbody.innerHTML = '';
                        data.customers.forEach(customer => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${escapeHtml(customer.name)}</td>
                                <td>${escapeHtml(customer.phone)}</td>
                                <td>${escapeHtml(customer.company || '-')}</td>
                                <td>${new Date(customer.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-small" onclick="editCustomer(${customer.id})">Edit</button>
                                    <button class="btn btn-success btn-small" onclick="callCustomer(${customer.id})">Call</button>
                                    <button class="btn btn-danger btn-small" onclick="deleteCustomer(${customer.id})">Delete</button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                        table.style.display = 'table';
                    }
                    loading.style.display = 'none';
                });
        }
        
        function showCustomerForm(customer = null) {
            const isEdit = customer !== null;
            const modalBody = document.getElementById('modal-body');
            
            modalBody.innerHTML = `
                <h3>${isEdit ? 'Edit Customer' : 'Add New Customer'}</h3>
                <form id="customer-form">
                    <input type="hidden" name="action" value="${isEdit ? 'edit' : 'add'}">
                    ${isEdit ? `<input type="hidden" name="id" value="${customer.id}">` : ''}
                    
                    <div class="form-group">
                        <label>Name</label>
                        <input type="text" name="name" value="${isEdit ? escapeHtml(customer.name) : ''}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" name="phone" value="${isEdit ? escapeHtml(customer.phone) : ''}" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" value="${isEdit ? escapeHtml(customer.email || '') : ''}">
                    </div>
                    
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" name="company" value="${isEdit ? escapeHtml(customer.company || '') : ''}">
                    </div>
                    
                    <div class="form-group">
                        <label>Notes</label>
                        <textarea name="notes" placeholder="Any additional notes...">${isEdit ? escapeHtml(customer.notes || '') : ''}</textarea>
                    </div>
                    
                    <div style="margin-top: 1rem;">
                        <button type="submit" class="btn btn-success">💾 Save Customer</button>
                        <button type="button" class="btn btn-danger" onclick="closeModal()">Cancel</button>
                    </div>
                </form>
            `;
            
            document.getElementById('modal').style.display = 'block';
            
            document.getElementById('customer-form').addEventListener('submit', function(e) {
                e.preventDefault();
                saveCustomer(new FormData(this));
            });
        }
        
        function editCustomer(id) {
            fetch('dashboard/manage_customers.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=get&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showCustomerForm(data.customer);
                } else {
                    showAlert('Error loading customer: ' + data.error, 'error');
                }
            });
        }
        
        function saveCustomer(formData) {
            fetch('dashboard/manage_customers.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    closeModal();
                    loadCustomers();
                } else {
                    showAlert('Error saving customer: ' + data.error, 'error');
                }
            });
        }
        
        function deleteCustomer(id) {
            if (!confirm('Are you sure you want to delete this customer?')) return;
            
            fetch('dashboard/manage_customers.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=delete&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    loadCustomers();
                } else {
                    showAlert('Error deleting customer: ' + data.error, 'error');
                }
            });
        }
        
        function callCustomer(id) {
            if (!confirm('Initiate call to this customer?')) return;
            
            showAlert('Initiating call...', 'info');
            
            fetch('dashboard/manage_customers.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `action=call&id=${id}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    refreshStatus();
                } else {
                    showAlert('Error initiating call: ' + data.error, 'error');
                }
            });
        }
        
        // Calls functions
        function loadCalls() {
            const loading = document.getElementById('calls-loading');
            const table = document.getElementById('calls-table');
            const tbody = document.getElementById('calls-tbody');
            
            loading.style.display = 'block';
            table.style.display = 'none';
            
            // Since we don't have a calls API endpoint yet, show sample data
            setTimeout(() => {
                tbody.innerHTML = `
                    <tr>
                        <td>2024-01-01 10:30</td>
                        <td>John Doe</td>
                        <td>+49123456789</td>
                        <td>5:32</td>
                        <td><span class="status-indicator status-online"></span>Successful</td>
                        <td>
                            <button class="btn btn-small">View Details</button>
                            <button class="btn btn-small">Listen</button>
                        </td>
                    </tr>
                `;
                table.style.display = 'table';
                loading.style.display = 'none';
            }, 500);
        }
        
        // Settings functions
        function loadSettings() {
            const loading = document.getElementById('settings-loading');
            const form = document.getElementById('settings-form');
            
            loading.style.display = 'block';
            form.style.display = 'none';
            
            fetch('dashboard/save_settings.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'action=get_settings'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateSettingsForm(data.settings);
                    form.style.display = 'block';
                }
                loading.style.display = 'none';
            });
            
            // Add form submit handler
            document.getElementById('settings-form').addEventListener('submit', function(e) {
                e.preventDefault();
                saveSettings(new FormData(this));
            });
        }
        
        function populateSettingsForm(settings) {
            const form = document.getElementById('settings-form');
            
            if (settings.database) {
                form.querySelector('[name="db_host"]').value = settings.database.host || 'localhost';
                form.querySelector('[name="db_name"]').value = settings.database.name || 'aiagent';
                form.querySelector('[name="db_user"]').value = settings.database.user || 'aiagent_user';
            }
            
            if (settings.asterisk) {
                form.querySelector('[name="asterisk_host"]').value = settings.asterisk.host || 'localhost';
                form.querySelector('[name="asterisk_port"]').value = settings.asterisk.port || 5038;
                form.querySelector('[name="asterisk_user"]').value = settings.asterisk.username || 'admin';
                form.querySelector('[name="caller_id"]').value = settings.asterisk.caller_id || 'AI Agent <1000>';
            }
            
            if (settings.call_settings) {
                form.querySelector('[name="max_duration"]').value = settings.call_settings.max_duration || 15;
                form.querySelector('[name="retry_attempts"]').value = settings.call_settings.retry_attempts || 3;
            }
        }
        
        function saveSettings(formData) {
            formData.append('action', 'save_settings');
            
            fetch('dashboard/save_settings.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                } else {
                    showAlert('Error saving settings: ' + data.error, 'error');
                }
            });
        }
        
        function testDatabase() {
            const form = document.getElementById('settings-form');
            const formData = new FormData(form);
            formData.append('action', 'test_database');
            
            showAlert('Testing database connection...', 'info');
            
            fetch('dashboard/save_settings.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Database connection successful!', 'success');
                } else {
                    showAlert('Database connection failed: ' + data.error, 'error');
                }
            });
        }
        
        function testAsterisk() {
            const form = document.getElementById('settings-form');
            const formData = new FormData(form);
            formData.append('action', 'test_asterisk');
            
            showAlert('Testing Asterisk connection...', 'info');
            
            fetch('dashboard/save_settings.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('Asterisk connection successful!', 'success');
                } else {
                    showAlert('Asterisk connection failed: ' + data.error, 'error');
                }
            });
        }
        
        // Utility functions
        function closeModal() {
            document.getElementById('modal').style.display = 'none';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function showAlert(message, type) {
            const alertContainer = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type === 'error' ? 'error' : type === 'success' ? 'success' : 'info'}`;
            alert.textContent = message;
            
            alertContainer.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('modal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>