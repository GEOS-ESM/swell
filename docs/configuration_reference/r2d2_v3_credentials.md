# R2D2 v3 Credentials Configuration

This document explains how to configure R2D2 v3 credentials for SWELL workflows.

## Overview

SWELL now uses R2D2 v3 for metadata-driven data storage and retrieval. R2D2 v3 requires authentication credentials to access the centralized API. SWELL automatically loads these credentials from a YAML configuration file.

## Quick Setup

1. **Create the credentials directory:**
   ```bash
   mkdir -p ~/.swell
   ```

2. **Create the credentials file:**
   ```bash
   cp /path/to/swell/r2d2_credentials.yaml ~/.swell/r2d2_credentials.yaml
   ```

3. **Edit with your credentials:**
   ```bash
   vim ~/.swell/r2d2_credentials.yaml
   ```

4. **Set secure permissions:**
   ```bash
   chmod 600 ~/.swell/r2d2_credentials.yaml
   ```

## Credentials File Format

Create `~/.swell/r2d2_credentials.yaml` with the following structure:

```yaml
# R2D2 v3 credentials file
# Save this as ~/.swell/r2d2_credentials.yaml
# Set permissions: chmod 600 ~/.swell/r2d2_credentials.yaml

# Required credentials
user: your_username              # Your R2D2 username
api_key: your_api_key            # Your R2D2 API key

# Platform-specific values (automatically determined by SWELL with an option to use YAML-first)
# host: discover-gmao            # Automatically set based on platform
# compiler: intel                # Automatically set based on platform

```

## Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `user` | Your R2D2 username | `jdoe` |
| `api_key` | Your R2D2 API authentication key | `abcd1234-ef56-7890-abcd-1234567890ab` |

## Platform-Specific Fields (Automatically Set)

| Field | Description | NCCS Discover Value |
|-------|-------------|---------------------|
| `host` | Compute host identifier | `discover-gmao` |
| `compiler` | Compiler type used | `intel` |

**Important**: `host` and `compiler` are automatically determined by SWELL based on your platform configuration. You can also set these manually in your credentials file.

### Loading Precedence

The credential loading follows this priority order:

1. **Environment Variables** (highest priority)
2. **YAML Configuration File** 
3. **Platform Detection** (for host/compiler only)

**For host and compiler specifically:**
- YAML `host`/`compiler` values override platform detection
- Platform detection is used as fallback when not specified in YAML

### Platform-Specific Configuration

SWELL automatically determines `host` and `compiler` based on your platform:

| Platform | R2D2 Host | R2D2 Compiler | Notes |
|----------|-----------|---------------|-------|
| `nccs_discover_sles15` | `discover-gmao` | `intel` | NCCS Discover SLES15 |
| `nccs_discover_cascade` | `discover-gmao` | `intel` | NCCS Discover Cascade |
<!-- | `aws` | `aws-gmao` | `intel` | AWS cloud platform |
| `generic` | `None` | `None` | Fallback to YAML/env vars | -->


## Environment Variables Set

When loaded, the following environment variables are set:

- `R2D2_USER`: Your R2D2 username
- `R2D2_API_KEY`: Your R2D2 API key  
- `R2D2_HOST`: Compute host name
- `R2D2_COMPILER`: Compiler type
<!-- - `R2D2_SERVER_HOST`: (Optional) API server override
- `R2D2_SERVER_PORT`: (Optional) API server port override -->

