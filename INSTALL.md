# AI Cold Calling Agent - Complete Installation Guide

This document provides comprehensive installation instructions for the AI Cold Calling Agent with Asterisk PBX and PHP Dashboard.

## 🚀 Automated Installation

### Prerequisites

- Ubuntu Server 22.04 LTS (fresh installation recommended)
- Root access (sudo privileges)
- Internet connection for package downloads
- At least 4GB RAM and 20GB storage space

### One-Command Installation

```bash
sudo bash install.sh
```

This script will automatically install and configure:

- ✅ **System Dependencies**: Python 3.8+, build tools, audio libraries
- ✅ **Database Systems**: PostgreSQL, MySQL, SQLite
- ✅ **Asterisk PBX**: Complete telephony system with AMI configuration
- ✅ **Web Server**: Apache with PHP and required extensions
- ✅ **AI Agent Application**: Python virtual environment with dependencies
- ✅ **PHP Dashboard**: Web-based management interface
- ✅ **System Services**: Automatic startup configuration

### Installation Process

The installation script performs these steps:

1. **System Update**: Updates all packages to latest versions
2. **Dependency Installation**: Installs required system packages
3. **Asterisk Setup**: Installs and configures Asterisk PBX with AMI
4. **Web Server Setup**: Configures Apache with PHP support
5. **Database Setup**: Creates databases and sample data
6. **AI Agent Installation**: Sets up Python environment and application
7. **Service Configuration**: Creates systemd services for auto-startup
8. **Security Setup**: Configures firewall rules
9. **Final Configuration**: Creates management scripts and documentation

## 🎛️ Dashboard Features

### Web Interface

Access the dashboard at: `http://your-server-ip/aiagent`

**Default Login:**
- Username: `admin`
- Password: `admin123`

### Dashboard Sections

#### 📊 **Dashboard Overview**
- Real-time system status (AI Agent, Asterisk, Database)
- Call statistics and performance metrics
- Quick action buttons for system control

#### 📝 **Scripts Management**
- Create and edit conversation scripts
- Organize by context (opening, questioning, presenting, objection handling, closing)
- Real-time script editing with syntax highlighting

#### ❓ **FAQ Management**
- Manage frequently asked questions and answers
- Categorize FAQs (general, pricing, technical, support)
- Quick search and filter functionality

#### 👥 **Customer Management**
- Add and manage customer contacts
- Track call history and notes
- One-click call initiation
- Customer segmentation and tagging

#### 📞 **Call Management**
- View call history and recordings
- Monitor active calls in real-time
- Call analytics and performance reports
- Export call data for analysis

#### ⚙️ **System Settings**
- Configure database connections
- Asterisk PBX settings
- Call parameters and limits
- System monitoring configuration

## 📞 Asterisk Configuration

### Default Configuration

The installation automatically configures Asterisk with:

```ini
# Manager Interface (AMI)
Host: localhost
Port: 5038
Username: admin
Password: aiagent_secret_2024

# SIP Configuration
Internal Extensions: 1000-1001 (for testing)
Outbound Context: outbound
Channel Technology: SIP/PJSIP support
```

### Testing Asterisk

```bash
# Connect to Asterisk CLI
sudo asterisk -r

# Test AMI connection
telnet localhost 5038

# Check SIP status
sip show peers

# Test internal call
dial 1000 (test extension)
```

## 🔧 Management Commands

### AI Agent Management

```bash
# Navigate to installation directory
cd ~/aiagent

# Start AI Agent
./admin.sh start

# Stop AI Agent
./admin.sh stop

# Check status
./admin.sh status

# View logs
./admin.sh logs

# Access dashboard
./admin.sh dashboard
```

### System Services

```bash
# AI Agent service
sudo systemctl start aiagent
sudo systemctl stop aiagent
sudo systemctl status aiagent

# Asterisk service
sudo systemctl start asterisk
sudo systemctl stop asterisk
sudo systemctl status asterisk

# Web server
sudo systemctl start apache2
sudo systemctl restart apache2
```

## 🔒 Security Configuration

### Change Default Passwords

1. **Dashboard Login**: Edit `dashboard_main.php` to change admin password
2. **Asterisk AMI**: Update `/etc/asterisk/manager.conf`
3. **Database**: Configure secure database passwords

### Firewall Setup

The installation configures UFW with these rules:
```bash
# Web traffic
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# Telephony
ufw allow 5060/udp  # SIP
ufw allow 5038/tcp  # Asterisk AMI

# Management
ufw allow ssh       # SSH access
```

### SSL/TLS Configuration (Recommended for Production)

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-apache

# Obtain SSL certificate
sudo certbot --apache -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Configuration Files

### Key Configuration Locations

```
~/aiagent/
├── config/config.yaml          # Main AI agent configuration
├── dashboard/                   # PHP dashboard files
├── admin.sh                    # Management script
└── logs/                       # Application logs

/etc/asterisk/
├── manager.conf                # AMI configuration
├── extensions.conf             # Dialplan
├── sip.conf                    # SIP configuration
└── pjsip.conf                  # PJSIP configuration

/var/www/html/aiagent/          # Web dashboard
```

### Database Configuration

```yaml
# config/config.yaml
database:
  type: mysql
  host: localhost
  port: 3306
  name: aiagent
  username: aiagent_user
  password: your_secure_password

asterisk:
  enabled: true
  host: localhost
  port: 5038
  username: admin
  password: aiagent_secret_2024
  channel_technology: SIP
  context: outbound
  caller_id: "AI Agent <1000>"
```

## 🎯 SIP Trunk Configuration

### Adding Your SIP Provider

Edit `/etc/asterisk/sip.conf`:

```ini
[your-provider]
type=friend
context=outbound
host=sip.your-provider.com
username=your-sip-username
secret=your-sip-password
fromuser=your-sip-username
fromdomain=sip.your-provider.com
insecure=port,invite
canreinvite=no
```

Then restart Asterisk:
```bash
sudo systemctl restart asterisk
```

## 📊 Monitoring and Maintenance

### Log Files

```bash
# AI Agent logs
tail -f ~/aiagent/logs/aiagent.log

# Asterisk logs
tail -f /var/log/asterisk/messages

# Apache logs
tail -f /var/log/apache2/access.log
tail -f /var/log/apache2/error.log

# System journal
sudo journalctl -u aiagent -f
sudo journalctl -u asterisk -f
```

### Performance Monitoring

The dashboard provides real-time monitoring of:
- Active call count
- Daily call statistics
- Success rates and KPIs
- System resource usage
- Database performance

### Backup Strategy

```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backup/aiagent-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup application
cp -r ~/aiagent $BACKUP_DIR/

# Backup database
mysqldump aiagent > $BACKUP_DIR/database.sql

# Backup Asterisk config
cp -r /etc/asterisk $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

## 🆘 Troubleshooting

### Common Issues

#### AI Agent Won't Start
```bash
# Check logs
./admin.sh logs

# Verify configuration
python3 run.py validate

# Check dependencies
source venv/bin/activate
pip list
```

#### Asterisk Connection Failed
```bash
# Check Asterisk status
sudo asterisk -r

# Test AMI connection
telnet localhost 5038

# Verify configuration
sudo asterisk -r -x "manager show settings"
```

#### Dashboard Not Accessible
```bash
# Check Apache status
sudo systemctl status apache2

# Check PHP errors
sudo tail -f /var/log/apache2/error.log

# Verify permissions
sudo chown -R www-data:www-data /var/www/html/aiagent
```

#### Database Connection Issues
```bash
# Test MySQL connection
mysql -u aiagent_user -p aiagent

# Check database status
sudo systemctl status mysql

# Reset database permissions
sudo mysql
> GRANT ALL ON aiagent.* TO 'aiagent_user'@'localhost';
> FLUSH PRIVILEGES;
```

### Getting Help

1. **Check logs** for error messages
2. **Run validation** commands to verify configuration
3. **Review documentation** in `docs/` directory
4. **Test individual components** separately
5. **Check system resources** (memory, disk space)

## 🔄 Updates and Maintenance

### Updating the AI Agent

```bash
cd ~/aiagent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
./admin.sh restart
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart services
sudo systemctl restart asterisk
./admin.sh restart
```

## 📞 Support and Documentation

- **Project Repository**: https://github.com/Pormetrixx/Aiagent
- **Documentation**: `docs/` directory
- **Configuration Examples**: `examples/` directory
- **Asterisk Setup Guide**: `docs/ASTERISK_SETUP.md`
- **API Documentation**: `docs/API.md`

---

**🎉 Congratulations!** Your AI Cold Calling Agent is now ready for production use with complete Asterisk PBX integration and web dashboard management.