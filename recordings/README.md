# Recordings Directory

This directory stores audio recordings from customer calls for analysis and training purposes.

## Structure

- `YYYY-MM-DD/` - Daily directories
  - `call_<id>/` - Individual call recordings
    - `full_call.wav` - Complete call recording
    - `turns/` - Individual conversation turns
      - `turn_001_customer.wav`
      - `turn_002_agent.wav`

## Privacy and Compliance

⚠️ **Important**: Recording customer calls may require legal compliance:

- **Consent**: Ensure you have proper consent to record
- **GDPR**: Comply with data protection regulations
- **Retention**: Set appropriate data retention policies
- **Security**: Encrypt recordings and limit access

## Configuration

Recording settings in `config/config.yaml`:

```yaml
call_settings:
  recording_enabled: true
  recording_path: "recordings/"
```

## Storage Management

- Recordings can consume significant disk space
- Implement automatic cleanup policies
- Consider compression for long-term storage
- Regular backups for important recordings

## File Formats

- Primary format: WAV (uncompressed)
- Sample rate: 16kHz or 44.1kHz
- Bit depth: 16-bit
- Channels: Mono preferred for analysis