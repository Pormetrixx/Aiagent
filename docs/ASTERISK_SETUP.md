# Asterisk Configuration for AI Cold Calling Agent

This document explains how to configure Asterisk to work with the AI Cold Calling Agent.

## Prerequisites

- Asterisk 16+ installed on Ubuntu Server 22.04 LTS
- Manager interface enabled
- SIP trunk configured for outbound calls

## Asterisk Configuration Files

### 1. manager.conf

Enable the Asterisk Manager Interface (AMI):

```ini
[general]
enabled = yes
port = 5038
bindaddr = 0.0.0.0

[admin]
secret = secret
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.0
permit=192.168.1.0/255.255.255.0
read = system,call,log,verbose,command,agent,user,config,command,dtmf,reporting,cdr,dialplan
write = system,call,log,verbose,command,agent,user,config,command,dtmf,reporting,cdr,dialplan
```

### 2. extensions.conf

Configure the outbound context for AI agent calls:

```ini
[outbound]
; AI Agent outbound calls
exten => s,1,NoOp(AI Agent Call Starting)
exten => s,n,Answer()
exten => s,n,Wait(1)
exten => s,n,Playback(silence/1)
exten => s,n,AGI(ai_agent_handler.py)
exten => s,n,Hangup()

; Direct dial for testing
exten => _X.,1,NoOp(Outbound call to ${EXTEN})
exten => _X.,n,Dial(SIP/trunk/${EXTEN},60)
exten => _X.,n,Hangup()

[internal]
; Internal extensions for testing
exten => 1000,1,Answer()
exten => 1000,n,Playback(demo-congrats)
exten => 1000,n,Hangup()
```

### 3. sip.conf (if using chan_sip)

```ini
[general]
context=default
allowoverlap=no
bindport=5060
bindaddr=0.0.0.0
srvlookup=yes

[trunk]
type=friend
context=outbound
host=your-sip-provider.com
username=your-username
secret=your-password
fromuser=your-username
fromdomain=your-sip-provider.com
insecure=port,invite
canreinvite=no
```

### 4. pjsip.conf (if using chan_pjsip - recommended)

```ini
[global]
type=global
endpoint_identifier_order=ip,username

[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[trunk]
type=endpoint
context=outbound
disallow=all
allow=ulaw
allow=alaw
allow=g722
outbound_auth=trunk_auth
aors=trunk

[trunk_auth]
type=auth
auth_type=userpass
username=your-username
password=your-password

[trunk]
type=aor
contact=sip:your-sip-provider.com
```

## AI Agent Configuration

Update your `config/config.yaml`:

```yaml
asterisk:
  enabled: true
  host: "localhost"        # Asterisk server IP
  port: 5038              # AMI port
  username: "admin"       # AMI username
  password: "secret"      # AMI password
  channel_technology: "SIP"  # or "PJSIP"
  context: "outbound"     # Dialplan context
  extension: "s"          # Extension to execute
  priority: 1             # Priority in dialplan
  caller_id: "AI Agent <1000>"
  trunk_pattern: "SIP/trunk"  # For direct dialing
```

## Testing the Configuration

### 1. Test AMI Connection

```bash
telnet localhost 5038
```

You should see:
```
Asterisk Call Manager/X.X.X
```

Login:
```
Action: Login
Username: admin
Secret: secret

```

### 2. Test Call Origination

```bash
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from src.telephony.asterisk import AsteriskTelephonyProvider

async def test():
    config = {
        'host': 'localhost',
        'port': 5038,
        'username': 'admin',
        'password': 'secret',
        'channel_technology': 'SIP',
        'context': 'outbound'
    }
    
    provider = AsteriskTelephonyProvider(config)
    if await provider.initialize():
        result = await provider.make_call('1000')  # Test extension
        print(f'Call result: {result}')
    await provider.cleanup()

asyncio.run(test())
"
```

## Security Considerations

1. **Firewall**: Only allow AMI connections from trusted IPs
2. **Authentication**: Use strong passwords for AMI users
3. **Permissions**: Limit AMI permissions to required actions only
4. **Network**: Consider VPN for remote connections

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if Asterisk is running: `sudo systemctl status asterisk`
   - Verify AMI is enabled: `asterisk -r -x "manager show settings"`

2. **Authentication Failed**
   - Check manager.conf credentials
   - Verify permit/deny rules
   - Reload manager: `asterisk -r -x "manager reload"`

3. **Call Origination Fails**
   - Check SIP trunk registration: `asterisk -r -x "sip show peers"`
   - Verify dialplan: `asterisk -r -x "dialplan show outbound"`
   - Check Asterisk logs: `tail -f /var/log/asterisk/messages`

### Asterisk CLI Commands

```bash
# Connect to Asterisk CLI
sudo asterisk -r

# Useful commands
manager show connected
sip show peers
dialplan show outbound
core show channels
```

## Advanced Configuration

### Call Recording

Add to extensions.conf:
```ini
[outbound]
exten => s,1,Set(AUDIOHOOK_INHERIT(MixMonitor)=yes)
exten => s,n,MixMonitor(/var/spool/asterisk/monitor/${UNIQUEID}.wav)
exten => s,n,NoOp(AI Agent Call Starting)
; ... rest of dialplan
```

### Call Queues

For handling multiple simultaneous calls:
```ini
[queues.conf]
[ai-agent-queue]
strategy = rrmemory
timeout = 300
retry = 5
maxlen = 0
announce-frequency = 30
```

This configuration enables the AI Cold Calling Agent to work seamlessly with a local Asterisk server for professional call management.