#!/bin/bash
# Complete installation script for AI Cold Calling Agent
# Installs all requirements, Asterisk PBX, and PHP dashboard

set -e

# Store original directory
ORIGINAL_DIR=$(pwd)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
INSTALL_DIR="$ACTUAL_HOME/aiagent"

log "🚀 Starting complete AI Cold Calling Agent installation"
log "📁 Installation directory: $INSTALL_DIR"
log "👤 Target user: $ACTUAL_USER"

# Update system packages
log "📦 Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install basic dependencies
log "🔧 Installing basic system dependencies..."
apt-get install -y \
    curl \
    wget \
    git \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    build-essential \
    cmake \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    libasound2-dev \
    ffmpeg \
    sox \
    sqlite3 \
    postgresql \
    postgresql-contrib \
    mysql-server \
    apache2 \
    php \
    php-mysql \
    php-pgsql \
    php-json \
    net-tools \
    php-mbstring \
    php-curl \
    php-zip \
    libapache2-mod-php

# Install Python 3.8+ if not available
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    log "📥 Installing Python 3.8+"
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update
    apt-get install -y python3.8 python3.8-venv python3.8-dev
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
fi

log "✅ Python version: $(python3 --version)"

# Install Asterisk PBX
log "📞 Installing Asterisk PBX..."

# Check if Asterisk is already installed
if command -v asterisk &> /dev/null; then
    log "✅ Asterisk already installed, checking version..."
    asterisk -V
else
    # Install Asterisk from Ubuntu repositories (more reliable)
    # This approach uses the official Ubuntu packages which are stable and tested
    log "📦 Installing Asterisk from Ubuntu repositories..."
    
    apt-get update
    
    # Install with error handling
    if apt-get install -y \
        asterisk \
        asterisk-modules \
        asterisk-config \
        asterisk-doc \
        asterisk-dev; then
        log "✅ Asterisk packages installed successfully"
    else
        log "❌ Failed to install Asterisk packages from repository"
        log "🔄 Trying alternative installation method..."
        
        # Install build dependencies
        apt-get install -y \
            build-essential \
            libssl-dev \
            libncurses-dev \
            libnewt-dev \
            libxml2-dev \
            linux-headers-$(uname -r) \
            libsqlite3-dev \
            uuid-dev \
            libjansson-dev \
            wget \
            tar
        
        # Download and install Asterisk from source
        cd /tmp
        ASTERISK_VERSION="18.15.0"
        log "📥 Downloading Asterisk $ASTERISK_VERSION source..."
        
        if wget "http://downloads.asterisk.org/pub/telephony/asterisk/releases/asterisk-${ASTERISK_VERSION}.tar.gz"; then
            tar -xzf "asterisk-${ASTERISK_VERSION}.tar.gz"
            cd "asterisk-${ASTERISK_VERSION}"
            
            log "🔨 Compiling Asterisk (this may take several minutes)..."
            ./configure --with-jansson-bundled
            make menuselect.makeopts
            make -j$(nproc)
            make install
            make samples
            make config
            
            log "✅ Asterisk compiled and installed from source"
        else
            log "❌ Failed to download Asterisk source"
            log "⚠️  You may need to install Asterisk manually"
        fi
        
        cd "$ORIGINAL_DIR"
    fi
fi

# Enable and start Asterisk
log "🚀 Starting Asterisk service..."
systemctl enable asterisk

# Start Asterisk and verify it's running
if systemctl start asterisk; then
    sleep 5
    if systemctl is-active asterisk --quiet; then
        log "✅ Asterisk service started successfully"
        asterisk_version=$(asterisk -V 2>/dev/null || echo "Version check failed")
        log "📋 Asterisk version: $asterisk_version"
        
        # Verify AMI port is listening
        if netstat -tlnp | grep -q ":5038"; then
            log "✅ Asterisk AMI port (5038) is listening"
        else
            warn "⚠️  Asterisk AMI port (5038) is not listening yet"
        fi
    else
        warn "⚠️  Asterisk service started but may not be fully operational"
    fi
else
    error "❌ Failed to start Asterisk service"
    log "🔍 Checking Asterisk status..."
    systemctl status asterisk || true
    
    # Try to get more information about the failure
    if [ -f /var/log/asterisk/messages ]; then
        log "📋 Recent Asterisk log entries:"
        tail -n 10 /var/log/asterisk/messages || true
    fi
fi

# Configure Asterisk for AI Agent
log "🔧 Configuring Asterisk for AI Agent..."

# Backup original configs
cp /etc/asterisk/manager.conf /etc/asterisk/manager.conf.backup
cp /etc/asterisk/extensions.conf /etc/asterisk/extensions.conf.backup
cp /etc/asterisk/sip.conf /etc/asterisk/sip.conf.backup

# Configure manager.conf for AMI
cat > /etc/asterisk/manager.conf << 'EOF'
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0
displayconnects = yes

[admin]
secret = aiagent_secret_2024
deny = 0.0.0.0/0.0.0.0
permit = 127.0.0.1/255.255.255.0
permit = 192.168.0.0/255.255.0.0
permit = 10.0.0.0/255.0.0.0
permit = 172.16.0.0/255.240.0.0
read = system,call,log,verbose,command,agent,user,config,dtmf,reporting,cdr,dialplan
write = system,call,log,verbose,command,agent,user,config,dtmf,reporting,cdr,dialplan
EOF

# Configure extensions.conf for outbound calls
cat > /etc/asterisk/extensions.conf << 'EOF'
[general]
static=yes
writeprotect=no
clearglobalvars=no

[globals]
CONSOLE=Console/dsp
IAXINFO=guest
TRUNK=SIP/trunk

[outbound]
; AI Agent outbound context
exten => s,1,NoOp(AI Agent Call Starting)
 same => n,Answer()
 same => n,Wait(1)
 same => n,Playback(silence/1)
 same => n,Set(CALL_ID=${UNIQUEID})
 same => n,UserEvent(AIAgentCallStart,CallID:${CALL_ID},Channel:${CHANNEL})
 same => n,Hangup()

; Direct outbound dialing pattern
exten => _X.,1,NoOp(Outbound call to ${EXTEN})
 same => n,Set(CALLERID(num)=1000)
 same => n,Set(CALLERID(name)=AI Agent)
 same => n,Dial(SIP/trunk/${EXTEN},60,tT)
 same => n,Hangup()

[internal]
; Internal test extensions
exten => 1000,1,Answer()
 same => n,Playback(demo-congrats)
 same => n,Wait(5)
 same => n,Hangup()

exten => 1001,1,Answer()
 same => n,Playback(hello-world)
 same => n,Echo()
 same => n,Hangup()

[default]
include => internal
include => outbound
EOF

# Basic SIP configuration
cat > /etc/asterisk/sip.conf << 'EOF'
[general]
context=default
allowoverlap=no
bindport=5060
bindaddr=0.0.0.0
srvlookup=yes
disallow=all
allow=ulaw
allow=alaw
allow=g722
localnet=192.168.0.0/255.255.0.0
localnet=10.0.0.0/255.0.0.0
localnet=172.16.0.0/255.240.0.0

; Internal test extension
[1000]
type=friend
secret=test123
context=internal
host=dynamic
canreinvite=no

[1001]
type=friend
secret=test123
context=internal
host=dynamic
canreinvite=no

; Trunk configuration (template - needs provider details)
;[trunk]
;type=friend
;context=outbound
;host=your-sip-provider.com
;username=your-username
;secret=your-password
;fromuser=your-username
;fromdomain=your-sip-provider.com
;insecure=port,invite
;canreinvite=no
EOF

# Restart Asterisk to apply configuration
systemctl restart asterisk

log "✅ Asterisk configured for AI Agent"

# Install AI Agent application
log "🤖 Installing AI Cold Calling Agent..."

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy application files if running from source directory
if [ -f "../pyproject.toml" ] && [ -f "../requirements.txt" ]; then
    log "📁 Copying application files from source..."
    cp -r ../* . 2>/dev/null || true
    chown -R $ACTUAL_USER:$ACTUAL_USER .
else
    # Clone from repository if not running from source
    log "📥 Cloning AI Agent repository..."
    su -c "git clone https://github.com/Pormetrixx/Aiagent.git ." $ACTUAL_USER
fi

# Install Python dependencies
log "🐍 Installing Python dependencies..."
su -c "python3 -m venv venv" $ACTUAL_USER
su -c "source venv/bin/activate && pip install --upgrade pip" $ACTUAL_USER
su -c "source venv/bin/activate && pip install -r requirements.txt" $ACTUAL_USER

# Create necessary directories
su -c "mkdir -p logs recordings models backups" $ACTUAL_USER

# Set up admin script
log "🔧 Setting up admin script..."
chown $ACTUAL_USER:$ACTUAL_USER admin.sh
chmod +x admin.sh

# Initialize configuration with Asterisk settings
log "⚙️ Initializing configuration..."
su -c "source venv/bin/activate && python3 run.py init" $ACTUAL_USER

# Update Asterisk configuration in the agent config
CONFIG_FILE="$INSTALL_DIR/config/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    # Update Asterisk settings in configuration
    python3 << EOF
import yaml

config_file = "$CONFIG_FILE"
try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Update Asterisk configuration
    config['asterisk'] = {
        'enabled': True,
        'host': 'localhost',
        'port': 5038,
        'username': 'admin',
        'password': 'aiagent_secret_2024',
        'channel_technology': 'SIP',
        'context': 'outbound',
        'extension': 's',
        'priority': 1,
        'caller_id': 'AI Agent <1000>',
        'trunk_pattern': 'SIP/trunk',
        'local_extension_range': '1000-1999'
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Asterisk configuration updated")
except Exception as e:
    print(f"⚠️ Could not update config: {e}")
EOF
fi

# Install and configure PHP dashboard
log "🌐 Installing PHP dashboard..."

# Create web dashboard directory
WEB_DIR="/var/www/html/aiagent"
mkdir -p "$WEB_DIR"

# Create PHP dashboard files
cat > "$WEB_DIR/index.php" << 'EOF'
<?php
session_start();

// Configuration
$config = [
    'db_host' => 'localhost',
    'db_name' => 'aiagent',
    'db_user' => 'aiagent_user',
    'db_pass' => 'aiagent_pass',
    'agent_config_path' => '/home/' . get_current_user() . '/aiagent/config/config.yaml'
];

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
    include 'login.php';
    exit;
}

// Dashboard content
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cold Calling Agent - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f4f4f4; }
        .header { background: #2c3e50; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
        .nav { background: #34495e; padding: 0.5rem 0; }
        .nav-menu { list-style: none; display: flex; }
        .nav-menu li { margin-right: 2rem; }
        .nav-menu a { color: white; text-decoration: none; padding: 0.5rem 1rem; display: block; border-radius: 3px; }
        .nav-menu a:hover, .nav-menu a.active { background: #2c3e50; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .card { background: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .btn { background: #3498db; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #2980b9; }
        .btn-danger { background: #e74c3c; }
        .btn-danger:hover { background: #c0392b; }
        .btn-success { background: #27ae60; }
        .btn-success:hover { background: #229954; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
        .form-group textarea { height: 120px; resize: vertical; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 0.5rem; }
        .status-online { background: #27ae60; }
        .status-offline { background: #e74c3c; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; font-weight: bold; }
        .table tr:hover { background: #f8f9fa; }
    </style>
    <script>
        function showSection(sectionId) {
            // Hide all sections
            const sections = document.querySelectorAll('.section');
            sections.forEach(section => section.style.display = 'none');
            
            // Show selected section
            document.getElementById(sectionId).style.display = 'block';
            
            // Update navigation
            const navLinks = document.querySelectorAll('.nav-menu a');
            navLinks.forEach(link => link.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function refreshStatus() {
            // In a real implementation, this would make an AJAX call to check system status
            location.reload();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshStatus, 30000);
    </script>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Cold Calling Agent Dashboard</h1>
        <div>
            <span>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?></span>
            <form method="post" style="display: inline; margin-left: 1rem;">
                <input type="hidden" name="action" value="logout">
                <button type="submit" class="btn btn-danger">Logout</button>
            </form>
        </div>
    </div>
    
    <nav class="nav">
        <ul class="nav-menu">
            <li><a href="#" onclick="showSection('dashboard')" class="active">Dashboard</a></li>
            <li><a href="#" onclick="showSection('scripts')">Scripts</a></li>
            <li><a href="#" onclick="showSection('faqs')">FAQs</a></li>
            <li><a href="#" onclick="showSection('customers')">Customers</a></li>
            <li><a href="#" onclick="showSection('calls')">Calls</a></li>
            <li><a href="#" onclick="showSection('settings')">Settings</a></li>
        </ul>
    </nav>
    
    <div class="container">
        <!-- Dashboard Section -->
        <div id="dashboard" class="section">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">0</div>
                    <div class="stat-label">Active Calls</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">0</div>
                    <div class="stat-label">Total Calls Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">0%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">0</div>
                    <div class="stat-label">Leads Generated</div>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>System Status</h3>
                    <p><span class="status-indicator status-offline"></span>AI Agent: Offline</p>
                    <p><span class="status-indicator status-offline"></span>Asterisk PBX: Checking...</p>
                    <p><span class="status-indicator status-offline"></span>Database: Checking...</p>
                    <button class="btn" onclick="refreshStatus()">Refresh Status</button>
                </div>
                
                <div class="card">
                    <h3>Quick Actions</h3>
                    <p><a href="#" class="btn">Start Agent</a></p>
                    <p><a href="#" class="btn btn-danger">Stop Agent</a></p>
                    <p><a href="#" onclick="showSection('calls')" class="btn btn-success">View Call Logs</a></p>
                </div>
            </div>
        </div>
        
        <!-- Scripts Section -->
        <div id="scripts" class="section" style="display: none;">
            <div class="card">
                <h3>Conversation Scripts</h3>
                <button class="btn" onclick="document.getElementById('script-form').style.display='block'">Add New Script</button>
                
                <div id="script-form" style="display: none; margin-top: 1rem; border: 1px solid #ddd; padding: 1rem; border-radius: 4px;">
                    <h4>Add/Edit Script</h4>
                    <form method="post" action="manage_scripts.php">
                        <div class="form-group">
                            <label>Script Name</label>
                            <input type="text" name="script_name" required>
                        </div>
                        <div class="form-group">
                            <label>Context</label>
                            <select name="context">
                                <option value="opening">Opening</option>
                                <option value="questioning">Questioning</option>
                                <option value="presenting">Presenting</option>
                                <option value="objection_handling">Objection Handling</option>
                                <option value="closing">Closing</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Script Content</label>
                            <textarea name="content" placeholder="Enter the script content here..."></textarea>
                        </div>
                        <button type="submit" class="btn">Save Script</button>
                        <button type="button" class="btn btn-danger" onclick="document.getElementById('script-form').style.display='none'">Cancel</button>
                    </form>
                </div>
                
                <table class="table" style="margin-top: 1rem;">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Context</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Default Opening</td>
                            <td>Opening</td>
                            <td>2024-01-01</td>
                            <td>
                                <a href="#" class="btn" style="padding: 0.25rem 0.5rem;">Edit</a>
                                <a href="#" class="btn btn-danger" style="padding: 0.25rem 0.5rem;">Delete</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- FAQs Section -->
        <div id="faqs" class="section" style="display: none;">
            <div class="card">
                <h3>Frequently Asked Questions</h3>
                <button class="btn" onclick="document.getElementById('faq-form').style.display='block'">Add New FAQ</button>
                
                <div id="faq-form" style="display: none; margin-top: 1rem; border: 1px solid #ddd; padding: 1rem; border-radius: 4px;">
                    <h4>Add/Edit FAQ</h4>
                    <form method="post" action="manage_faqs.php">
                        <div class="form-group">
                            <label>Question</label>
                            <input type="text" name="question" required>
                        </div>
                        <div class="form-group">
                            <label>Answer</label>
                            <textarea name="answer" placeholder="Enter the answer here..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Category</label>
                            <select name="category">
                                <option value="general">General</option>
                                <option value="pricing">Pricing</option>
                                <option value="technical">Technical</option>
                                <option value="support">Support</option>
                            </select>
                        </div>
                        <button type="submit" class="btn">Save FAQ</button>
                        <button type="button" class="btn btn-danger" onclick="document.getElementById('faq-form').style.display='none'">Cancel</button>
                    </form>
                </div>
                
                <table class="table" style="margin-top: 1rem;">
                    <thead>
                        <tr>
                            <th>Question</th>
                            <th>Category</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>What is your pricing?</td>
                            <td>Pricing</td>
                            <td>2024-01-01</td>
                            <td>
                                <a href="#" class="btn" style="padding: 0.25rem 0.5rem;">Edit</a>
                                <a href="#" class="btn btn-danger" style="padding: 0.25rem 0.5rem;">Delete</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Customers Section -->
        <div id="customers" class="section" style="display: none;">
            <div class="card">
                <h3>Customer Management</h3>
                <button class="btn" onclick="document.getElementById('customer-form').style.display='block'">Add New Customer</button>
                
                <div id="customer-form" style="display: none; margin-top: 1rem; border: 1px solid #ddd; padding: 1rem; border-radius: 4px;">
                    <h4>Add/Edit Customer</h4>
                    <form method="post" action="manage_customers.php">
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name" required>
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" name="phone" required>
                        </div>
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" name="email">
                        </div>
                        <div class="form-group">
                            <label>Company</label>
                            <input type="text" name="company">
                        </div>
                        <div class="form-group">
                            <label>Notes</label>
                            <textarea name="notes" placeholder="Any additional notes..."></textarea>
                        </div>
                        <button type="submit" class="btn">Save Customer</button>
                        <button type="button" class="btn btn-danger" onclick="document.getElementById('customer-form').style.display='none'">Cancel</button>
                    </form>
                </div>
                
                <table class="table" style="margin-top: 1rem;">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Company</th>
                            <th>Last Contact</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>John Doe</td>
                            <td>+49123456789</td>
                            <td>Example Corp</td>
                            <td>2024-01-01</td>
                            <td>
                                <a href="#" class="btn" style="padding: 0.25rem 0.5rem;">Edit</a>
                                <a href="#" class="btn btn-success" style="padding: 0.25rem 0.5rem;">Call</a>
                                <a href="#" class="btn btn-danger" style="padding: 0.25rem 0.5rem;">Delete</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Calls Section -->
        <div id="calls" class="section" style="display: none;">
            <div class="card">
                <h3>Call History</h3>
                <table class="table">
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
                    <tbody>
                        <tr>
                            <td>2024-01-01 10:30</td>
                            <td>John Doe</td>
                            <td>+49123456789</td>
                            <td>5:32</td>
                            <td><span class="status-indicator status-online"></span>Successful</td>
                            <td>
                                <a href="#" class="btn" style="padding: 0.25rem 0.5rem;">View Details</a>
                                <a href="#" class="btn" style="padding: 0.25rem 0.5rem;">Listen</a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Settings Section -->
        <div id="settings" class="section" style="display: none;">
            <div class="card">
                <h3>System Settings</h3>
                <form method="post" action="save_settings.php">
                    <div class="form-group">
                        <label>Database Host</label>
                        <input type="text" name="db_host" value="localhost">
                    </div>
                    <div class="form-group">
                        <label>Database Name</label>
                        <input type="text" name="db_name" value="aiagent">
                    </div>
                    <div class="form-group">
                        <label>Asterisk Host</label>
                        <input type="text" name="asterisk_host" value="localhost">
                    </div>
                    <div class="form-group">
                        <label>Asterisk AMI Port</label>
                        <input type="number" name="asterisk_port" value="5038">
                    </div>
                    <div class="form-group">
                        <label>Default Caller ID</label>
                        <input type="text" name="caller_id" value="AI Agent <1000>">
                    </div>
                    <div class="form-group">
                        <label>Max Call Duration (minutes)</label>
                        <input type="number" name="max_duration" value="15">
                    </div>
                    <button type="submit" class="btn">Save Settings</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
EOF

# Create login page
cat > "$WEB_DIR/login.php" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Cold Calling Agent - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); width: 100%; max-width: 400px; }
        .login-header { text-align: center; margin-bottom: 2rem; }
        .login-header h1 { color: #2c3e50; margin-bottom: 0.5rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #2c3e50; }
        .form-group input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
        .btn { width: 100%; background: #3498db; color: white; padding: 0.75rem; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        .btn:hover { background: #2980b9; }
        .error { color: #e74c3c; text-align: center; margin-bottom: 1rem; }
        .info { color: #7f8c8d; text-align: center; margin-top: 1rem; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🤖 AI Agent Dashboard</h1>
            <p>Cold Calling Management System</p>
        </div>
        
        <?php if (isset($login_error)): ?>
            <div class="error"><?php echo htmlspecialchars($login_error); ?></div>
        <?php endif; ?>
        
        <form method="post">
            <input type="hidden" name="action" value="login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        
        <div class="info">
            Default credentials: admin / admin123
        </div>
    </div>
</body>
</html>
EOF

# Create database management scripts
cat > "$WEB_DIR/db_setup.php" << 'EOF'
<?php
// Database setup script for AI Agent dashboard

function setupDatabase() {
    $config = [
        'host' => 'localhost',
        'user' => 'root',
        'pass' => '',
        'db_name' => 'aiagent'
    ];
    
    try {
        // Connect to MySQL
        $pdo = new PDO("mysql:host={$config['host']}", $config['user'], $config['pass']);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Create database if it doesn't exist
        $pdo->exec("CREATE DATABASE IF NOT EXISTS {$config['db_name']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
        $pdo->exec("USE {$config['db_name']}");
        
        // Create tables
        $tables = [
            'scripts' => "
                CREATE TABLE IF NOT EXISTS scripts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    context VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ",
            'faqs' => "
                CREATE TABLE IF NOT EXISTS faqs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category VARCHAR(100) DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ",
            'customers' => "
                CREATE TABLE IF NOT EXISTS customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    company VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_phone (phone)
                )
            ",
            'calls' => "
                CREATE TABLE IF NOT EXISTS calls (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    phone VARCHAR(50) NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    duration INT DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'initiated',
                    notes TEXT,
                    recording_path VARCHAR(500),
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
                )
            "
        ];
        
        foreach ($tables as $table => $sql) {
            $pdo->exec($sql);
            echo "✅ Table '$table' created successfully\n";
        }
        
        // Insert sample data
        $sample_data = [
            "INSERT IGNORE INTO scripts (name, context, content) VALUES 
                ('Default Opening', 'opening', 'Hello, this is [Agent Name] from [Company]. How are you today?'),
                ('Price Objection', 'objection_handling', 'I understand price is important. Let me explain the value...')",
            
            "INSERT IGNORE INTO faqs (question, answer, category) VALUES 
                ('What is your pricing?', 'Our pricing starts at €99/month for the basic package.', 'pricing'),
                ('Do you offer support?', 'Yes, we provide 24/7 customer support via phone and email.', 'support')",
            
            "INSERT IGNORE INTO customers (name, phone, email, company) VALUES 
                ('John Doe', '+49123456789', 'john@example.com', 'Example Corp'),
                ('Jane Smith', '+49987654321', 'jane@test.com', 'Test GmbH')"
        ];
        
        foreach ($sample_data as $sql) {
            $pdo->exec($sql);
        }
        
        echo "✅ Database setup completed successfully\n";
        return true;
        
    } catch (PDOException $e) {
        echo "❌ Database error: " . $e->getMessage() . "\n";
        return false;
    }
}

// Run setup if called directly
if (php_sapi_name() === 'cli') {
    setupDatabase();
}
?>
EOF

# Set up web server permissions
chown -R www-data:www-data "$WEB_DIR"
chmod -R 755 "$WEB_DIR"

# Enable Apache mod_rewrite
a2enmod rewrite
systemctl restart apache2

# Setup database
cd "$WEB_DIR"
php db_setup.php

log "✅ PHP dashboard installed at http://localhost/aiagent"

# Create systemd service for AI Agent
log "🔧 Creating systemd service..."

cat > /etc/systemd/system/aiagent.service << EOF
[Unit]
Description=AI Cold Calling Agent
After=network.target asterisk.service
Requires=asterisk.service

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/run.py start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable aiagent.service

log "✅ Systemd service created and enabled"

# Create firewall rules
log "🔒 Configuring firewall..."
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5060/udp  # SIP
ufw allow 5038/tcp  # Asterisk AMI
ufw allow ssh

log "✅ Firewall configured"

# Final configuration
log "📝 Final configuration..."

# Create admin script for easy management
cat > "$INSTALL_DIR/admin.sh" << EOF
#!/bin/bash
# AI Agent administration script

case "\$1" in
    start)
        sudo systemctl start aiagent
        sudo systemctl start asterisk
        echo "✅ AI Agent and Asterisk started"
        ;;
    stop)
        sudo systemctl stop aiagent
        echo "✅ AI Agent stopped"
        ;;
    restart)
        sudo systemctl restart aiagent
        sudo systemctl restart asterisk
        echo "✅ AI Agent and Asterisk restarted"
        ;;
    status)
        echo "AI Agent status:"
        sudo systemctl status aiagent --no-pager
        echo ""
        echo "Asterisk status:"
        sudo systemctl status asterisk --no-pager
        ;;
    logs)
        sudo journalctl -u aiagent -f
        ;;
    asterisk)
        sudo asterisk -r
        ;;
    dashboard)
        echo "Dashboard URL: http://\$(hostname -I | awk '{print \$1}')/aiagent"
        echo "Default login: admin / admin123"
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|asterisk|dashboard}"
        exit 1
        ;;
esac
EOF

chmod +x "$INSTALL_DIR/admin.sh"
chown $ACTUAL_USER:$ACTUAL_USER "$INSTALL_DIR/admin.sh"

# Print installation summary
log "🎉 Installation completed successfully!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🤖 AI COLD CALLING AGENT - INSTALLATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📁 Installation Directory: $INSTALL_DIR"
echo "🌐 Web Dashboard: http://$(hostname -I | awk '{print $1}')/aiagent"
echo "👤 Dashboard Login: admin / admin123"
echo ""
echo "🔧 Management Commands:"
echo "  $INSTALL_DIR/admin.sh start     # Start AI Agent"
echo "  $INSTALL_DIR/admin.sh stop      # Stop AI Agent"
echo "  $INSTALL_DIR/admin.sh status    # Check status"
echo "  $INSTALL_DIR/admin.sh logs      # View logs"
echo "  $INSTALL_DIR/admin.sh dashboard # Show dashboard URL"
echo ""
echo "📞 Asterisk Commands:"
echo "  sudo asterisk -r               # Connect to Asterisk CLI"
echo "  $INSTALL_DIR/admin.sh asterisk # Quick CLI access"
echo ""
echo "🔧 Configuration Files:"
echo "  $INSTALL_DIR/config/config.yaml        # AI Agent config"
echo "  /etc/asterisk/manager.conf              # Asterisk AMI"
echo "  /etc/asterisk/extensions.conf           # Dialplan"
echo "  /etc/asterisk/sip.conf                  # SIP config"
echo ""
echo "🚀 Next Steps:"
echo "1. Configure your SIP trunk in /etc/asterisk/sip.conf"
echo "2. Update database settings in $INSTALL_DIR/config/config.yaml"
echo "3. Access web dashboard to manage scripts and FAQs"
echo "4. Start the system: $INSTALL_DIR/admin.sh start"
echo ""
echo "📖 Documentation:"
echo "  $INSTALL_DIR/docs/ASTERISK_SETUP.md    # Detailed setup guide"
echo "  $INSTALL_DIR/README.md                 # Project overview"
echo ""
echo "⚠️  Security Notes:"
echo "- Change default dashboard password immediately"
echo "- Configure firewall rules for your network"
echo "- Update Asterisk AMI password in both configs"
echo "- Set up SSL/TLS for production use"
echo ""
echo "═══════════════════════════════════════════════════════════════"

# Start services
log "🚀 Starting services..."
systemctl start asterisk
sleep 5

# Final validation
if su -c "cd $INSTALL_DIR && source venv/bin/activate && python3 run.py validate" $ACTUAL_USER; then
    echo ""
    log "✅ Installation completed successfully!"
else
    echo ""
    warn "⚠️  Installation completed but validation failed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- Check Asterisk status: systemctl status asterisk"
    echo "- Check AMI connection: telnet localhost 5038"
    echo "- Check logs: tail -f /var/log/asterisk/messages"
    echo "- Verify config: $INSTALL_DIR/config/config.yaml"
    echo ""
fi

echo ""
log "✅ Installation complete! Access the dashboard at http://$(hostname -I | awk '{print $1}')/aiagent"