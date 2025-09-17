#!/bin/bash
# AI Agent Administration Script
# Provides easy management commands for the AI Cold Calling Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/aiagent"
USER="aiagent"

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

# Function to check if running as correct user
check_user() {
    if [ "$EUID" -eq 0 ]; then
        error "This script should not be run as root"
        error "Please run as the aiagent user: su - aiagent -c './admin.sh $1'"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "AI Cold Calling Agent Administration Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the AI agent"
    echo "  stop        Stop the AI agent"
    echo "  restart     Restart the AI agent"
    echo "  status      Show system status"
    echo "  logs        Show recent logs"
    echo "  validate    Validate system configuration"
    echo "  dashboard   Show dashboard URL and login info"
    echo "  asterisk    Show Asterisk status and commands"
    echo "  backup      Create configuration backup"
    echo "  help        Show this help message"
    echo ""
}

# Function to start the agent
start_agent() {
    log "🚀 Starting AI Cold Calling Agent..."
    
    cd "$INSTALL_DIR"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        if python3 run.py start; then
            log "✅ AI Agent started successfully"
        else
            error "❌ Failed to start AI Agent"
            return 1
        fi
    else
        error "Virtual environment not found. Please reinstall."
        return 1
    fi
}

# Function to stop the agent
stop_agent() {
    log "🛑 Stopping AI Cold Calling Agent..."
    
    # Kill any running Python processes for the agent
    pkill -f "python3 run.py" || true
    pkill -f "python3 src/main.py" || true
    
    log "✅ AI Agent stopped"
}

# Function to show status
show_status() {
    echo "📊 System Status Report"
    echo "═══════════════════════════════════════"
    
    # Check Asterisk
    if systemctl is-active asterisk --quiet; then
        echo -e "Asterisk PBX: ${GREEN}✅ Running${NC}"
        asterisk_version=$(asterisk -V 2>/dev/null || echo "Unknown")
        echo "  Version: $asterisk_version"
    else
        echo -e "Asterisk PBX: ${RED}❌ Stopped${NC}"
    fi
    
    # Check AMI port
    if netstat -tlnp 2>/dev/null | grep -q ":5038"; then
        echo -e "AMI Port 5038: ${GREEN}✅ Listening${NC}"
    else
        echo -e "AMI Port 5038: ${RED}❌ Not listening${NC}"
    fi
    
    # Check Apache
    if systemctl is-active apache2 --quiet; then
        echo -e "Web Server: ${GREEN}✅ Running${NC}"
    else
        echo -e "Web Server: ${RED}❌ Stopped${NC}"
    fi
    
    # Check AI Agent
    if pgrep -f "python3 run.py" > /dev/null; then
        echo -e "AI Agent: ${GREEN}✅ Running${NC}"
    else
        echo -e "AI Agent: ${RED}❌ Stopped${NC}"
    fi
    
    # Check database connections
    echo ""
    echo "💾 Database Status:"
    if command -v mysql &> /dev/null; then
        if systemctl is-active mysql --quiet; then
            echo -e "MySQL: ${GREEN}✅ Running${NC}"
        else
            echo -e "MySQL: ${RED}❌ Stopped${NC}"
        fi
    fi
    
    if command -v postgresql-12 &> /dev/null || command -v postgres &> /dev/null; then
        if systemctl is-active postgresql --quiet; then
            echo -e "PostgreSQL: ${GREEN}✅ Running${NC}"
        else
            echo -e "PostgreSQL: ${RED}❌ Stopped${NC}"
        fi
    fi
    
    echo ""
    echo "📁 Installation Directory: $INSTALL_DIR"
    echo "👤 Current User: $(whoami)"
    echo "🕒 Uptime: $(uptime -p)"
}

# Function to show logs
show_logs() {
    echo "📋 Recent AI Agent Logs:"
    echo "═══════════════════════════════════════"
    
    if [ -f "$INSTALL_DIR/logs/agent.log" ]; then
        tail -n 20 "$INSTALL_DIR/logs/agent.log"
    else
        warn "No agent logs found"
    fi
    
    echo ""
    echo "📋 Recent Asterisk Logs:"
    echo "═══════════════════════════════════════"
    
    if [ -f "/var/log/asterisk/messages" ]; then
        sudo tail -n 10 /var/log/asterisk/messages 2>/dev/null || echo "Cannot access Asterisk logs (requires sudo)"
    else
        warn "No Asterisk logs found"
    fi
}

# Function to validate configuration
validate_config() {
    log "🔍 Validating system configuration..."
    
    cd "$INSTALL_DIR"
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        python3 run.py validate
    else
        error "Virtual environment not found"
        return 1
    fi
}

# Function to show dashboard info
show_dashboard() {
    echo "🌐 Dashboard Information"
    echo "═══════════════════════════════════════"
    
    IP=$(hostname -I | awk '{print $1}' || echo "localhost")
    echo "URL: http://$IP/aiagent"
    echo "Default Login: admin"
    echo "Default Password: admin123"
    echo ""
    echo "⚠️  Remember to change the default password!"
    echo ""
    echo "Dashboard Features:"
    echo "• Real-time system monitoring"
    echo "• Conversation script management"
    echo "• FAQ database editing"
    echo "• Customer management"
    echo "• Call analytics"
    echo "• System configuration"
}

# Function to show Asterisk commands
show_asterisk() {
    echo "📞 Asterisk Management"
    echo "═══════════════════════════════════════"
    
    echo "Status Commands:"
    echo "  sudo systemctl status asterisk    # Service status"
    echo "  sudo asterisk -rvvv               # Connect to CLI"
    echo "  sudo asterisk -rx 'core show version'  # Version"
    echo "  sudo asterisk -rx 'sip show peers'     # SIP peers"
    echo ""
    
    echo "Configuration Files:"
    echo "  /etc/asterisk/manager.conf        # AMI configuration"
    echo "  /etc/asterisk/extensions.conf     # Dialplan"
    echo "  /etc/asterisk/sip.conf           # SIP configuration"
    echo ""
    
    echo "Test AMI Connection:"
    echo "  telnet localhost 5038"
    echo "  (Use admin / aiagent_secret_2024)"
}

# Function to create backup
create_backup() {
    log "💾 Creating configuration backup..."
    
    BACKUP_DIR="$INSTALL_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup AI Agent config
    if [ -f "$INSTALL_DIR/config/config.yaml" ]; then
        cp "$INSTALL_DIR/config/config.yaml" "$BACKUP_DIR/"
        log "✅ AI Agent config backed up"
    fi
    
    # Backup Asterisk configs (requires sudo)
    if sudo cp /etc/asterisk/{manager.conf,extensions.conf,sip.conf} "$BACKUP_DIR/" 2>/dev/null; then
        log "✅ Asterisk configs backed up"
    else
        warn "Could not backup Asterisk configs (requires sudo)"
    fi
    
    log "📁 Backup created in: $BACKUP_DIR"
}

# Main command handler
case "${1:-help}" in
    start)
        check_user
        start_agent
        ;;
    stop)
        check_user
        stop_agent
        ;;
    restart)
        check_user
        stop_agent
        sleep 2
        start_agent
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    validate)
        check_user
        validate_config
        ;;
    dashboard)
        show_dashboard
        ;;
    asterisk)
        show_asterisk
        ;;
    backup)
        check_user
        create_backup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac