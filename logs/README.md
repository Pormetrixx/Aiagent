# Logs Directory

This directory contains application logs for the AI Cold Calling Agent.

## Log Files

- `aiagent.log` - Main application log
- `aiagent.log.1`, `aiagent.log.2`, etc. - Rotated log files

## Log Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General information about application flow
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

## Configuration

Log configuration is managed in `config/config.yaml`:

```yaml
logging:
  level: "INFO"
  file_path: "logs/aiagent.log"
  max_file_size_mb: 100
  backup_count: 5
```

## Monitoring

Logs are automatically rotated when they reach the configured size limit. Monitor logs for:
- Call success/failure rates
- Database connection issues
- Speech processing errors
- Training progress