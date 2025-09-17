#!/bin/bash
# Setup script for AI Cold Calling Agent

set -e

echo "Setting up AI Cold Calling Agent..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Error: Python 3.8+ is required, but found Python $python_version"
    exit 1
fi

echo "✓ Python version check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p recordings
mkdir -p models

echo "✓ Directories created"

# Initialize configuration
echo "Initializing configuration..."
python3 run.py init

echo "✓ Configuration initialized"

# Create systemd service file (optional)
create_systemd_service() {
    SERVICE_FILE="/etc/systemd/system/aiagent.service"
    CURRENT_DIR=$(pwd)
    USER=$(whoami)
    
    if [ "$EUID" -eq 0 ]; then
        cat > $SERVICE_FILE << EOF
[Unit]
Description=AI Cold Calling Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/run.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable aiagent.service
        
        echo "✓ Systemd service created and enabled"
        echo "  Start with: sudo systemctl start aiagent"
        echo "  Stop with: sudo systemctl stop aiagent"
        echo "  View logs with: sudo journalctl -u aiagent -f"
    else
        echo "⚠ Run with sudo to create systemd service"
    fi
}

# Ask if user wants to create systemd service
read -p "Create systemd service for automatic startup? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    create_systemd_service
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml with your database and model settings"
echo "2. Setup your PostgreSQL/MySQL database"
echo "3. Run the configuration validator: python3 run.py validate"
echo "4. Start the agent: python3 run.py start"
echo ""
echo "For development:"
echo "  source venv/bin/activate  # Activate virtual environment"
echo "  python3 run.py start     # Start the agent"
echo ""