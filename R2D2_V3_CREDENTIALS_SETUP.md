# R2D2 v3 Credentials Setup for SWELL

## Overview

SWELL now uses R2D2 v3 API for metadata storage and retrieval. This requires proper authentication credentials to be configured.

## Configuration File

Create a credentials file at `~/.swell/r2d2_credentials.yaml`:

```bash
# Create the .swell directory if it doesn't exist
mkdir -p ~/.swell

# Create the credentials file
cat > ~/.swell/r2d2_credentials.yaml << EOF
# R2D2 v3 API credentials
user: your_username
api_key: your_api_key_here

# Platform configuration  
host: discover-gmao
compiler: intel

# Optional: Override default API endpoint (usually not needed)
# server_host: https://r2d2-api.jcsda.org
# server_port: 443
EOF

# Set secure permissions
chmod 600 ~/.swell/r2d2_credentials.yaml
```

## Required Fields

- **user**: Your R2D2 username (provided by JEDI INFRA)
- **api_key**: Your R2D2 API key (provided by JEDI INFRA)
- **host**: Platform hostname (e.g., `discover-gmao`)
- **compiler**: Compiler used (e.g., `intel`)

## How It Works

1. **Automatic Loading**: SWELL tasks automatically load credentials from `~/.swell/r2d2_credentials.yaml`
2. **Environment Precedence**: Existing environment variables take precedence over config file
3. **Fallback**: If no config file exists, SWELL uses existing environment variables
4. **Smart Fallback**: SWELL tries R2D2 v3 API first, then falls back to local R2D2 v1 storage if files are not found

### Fallback Mechanism

SWELL implements a **smart fallback system** that ensures seamless migration from R2D2 v1 to v3:

1. **Primary**: Attempts to fetch data from R2D2 v3 API (centralized storage)
2. **Fallback**: If file not found in v3, automatically falls back to local R2D2 v1 storage
3. **Transparent**: This happens automatically - no user intervention required

This means:
- **New data** gets stored in R2D2 v3 (centralized)
- **Legacy data** remains accessible from local R2D2 v1 storage
- **Migration** happens gradually without breaking existing workflows

## Getting Credentials

Contact JEDI INFRA to obtain:
- Your R2D2 username
- Your R2D2 API key

## Troubleshooting

### Missing Credentials
```
R2D2 credentials file not found at ~/.swell/r2d2_credentials.yaml
R2D2 v3 will use existing environment variables if set
```

**Solution**: Create the credentials file as shown above.

### Authentication Errors
```
KeyError: A value must be set for $R2D2_USER
```

**Solution**: Verify your credentials file has the correct format and required fields.

### API Connection Issues
```
HTTP Request Error Message: 401 Unauthorized
```

**Solution**: Verify your API key is correct and contact JEDI INFRA if needed.

## Migration from Shell Scripts

If you previously used `.swell_r2d2_credentials.sh`, you can migrate by:

1. Extracting values from your shell script
2. Creating the YAML file with those values
3. Removing the old shell script

## Example Migration

Old shell script:
```bash
export R2D2_USER=myuser
export R2D2_API_KEY=1234567890
export R2D2_HOST=discover-gmao
export R2D2_COMPILER=intel
```

New YAML file:
```yaml
user: myuser
api_key: 1234567890
host: discover-gmao
compiler: intel
```

## Related Documentation

- [JCSDA R2D2 Documentation](https://github.com/JCSDA-internal/R2D2)
- SWELL R2D2 v3 Migration Guide
- SWELL Task Documentation

