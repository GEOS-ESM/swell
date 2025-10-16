#!/usr/bin/env python3

import r2d2
import os
import yaml

# Load R2D2 credentials from SWELL config file
config_path = os.path.expanduser("~/.swell/r2d2_credentials.yaml")
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        creds = yaml.safe_load(f)
    user = creds.get('user', os.environ.get('R2D2_USER'))
    host = creds.get('host', os.environ.get('R2D2_HOST'))
    compiler = creds.get('compiler', os.environ.get('R2D2_COMPILER'))
    if 'api_key' in creds:
        os.environ['R2D2_API_KEY'] = creds['api_key']
else:
    # Fallback to environment variables
    user = os.environ['R2D2_USER']
    host = os.environ['R2D2_HOST']  
    compiler = os.environ['R2D2_COMPILER']

compute_host = f"{host}-{compiler}"

# Try lifetime categories
for lifetime in ['debug', 'science', 'publication', 'release']:
    try:
        r2d2.register(
            item='experiment',
            name='swell-3dvar',
            compute_host=compute_host,
            user=user,
            lifetime=lifetime
        )
        print(f"✓ Registered swell-3dvar with lifetime: {lifetime}")
        break
    except Exception as e:
        if 'already' in str(e).lower():
            print("✓ swell-3dvar already registered")
            break
        print(f"✗ {lifetime}: {e}")
else:
    print("✗ Failed to register with any lifetime")
