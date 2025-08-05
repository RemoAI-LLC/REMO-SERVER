#!/bin/bash

# REMO-SERVER AWS EC2 Deployment Script
# This script sets up the environment and starts the FastAPI server

set -e  # Exit on any error

echo "🚀 Starting REMO-SERVER deployment on AWS EC2..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies for Python packages
echo "🔧 Installing system dependencies..."
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Install AWS CLI
echo "☁️ Installing AWS CLI..."
sudo apt-get install -y awscli

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/remo-server
sudo chown $USER:$USER /opt/remo-server

# Copy application files (assuming they're in the current directory)
echo "📋 Copying application files..."
cp -r . /opt/remo-server/
cd /opt/remo-server

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/remo-server.service > /dev/null <<EOF
[Unit]
Description=REMO AI Assistant API Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/remo-server
Environment=PATH=/opt/remo-server/venv/bin
ExecStart=/opt/remo-server/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
echo "🔄 Enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable remo-server

echo "✅ REMO-SERVER deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure AWS credentials:"
echo "   aws configure"
echo ""
echo "2. Edit setup_env.py with your actual values:"
echo "   nano setup_env.py"
echo ""
echo "3. Create Parameter Store entries:"
echo "   python3 setup_env.py create"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl start remo-server"
echo ""
echo "5. Check service status:"
echo "   sudo systemctl status remo-server"
echo ""
echo "📋 Useful commands:"
echo "  sudo systemctl status remo-server    # Check service status"
echo "  sudo systemctl stop remo-server      # Stop the service"
echo "  sudo systemctl start remo-server     # Start the service"
echo "  sudo systemctl restart remo-server   # Restart the service"
echo "  sudo journalctl -u remo-server -f    # View logs"
echo ""
echo "🌐 Once configured, server will be available at:"
echo "  http://your-ec2-ip:8000"
echo "  http://your-ec2-ip:8000/docs (API documentation)" 