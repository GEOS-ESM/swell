"""
Simple generic script to register observation files to r2d2 v3
Works for ncdiag, odas, gdas_marine, etc.
"""

import os
import sys
import glob

# Color codes for printing
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

try:
    import r2d2
except ImportError as e:
    raise ImportError(f"Failed to import r2d2: {e}\nLoad module: module load r2d2-client/sles15_0604")

REGISTERED_FILE = "registered_files.txt"

def load_registered():
    if os.path.exists(REGISTERED_FILE):
        with open(REGISTERED_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()


def save_registered(filename):
    with open(REGISTERED_FILE, 'a') as f:
        f.write(filename + '\n')


def guess_provider_from_path(file_path):
    """Find provider from file path"""
    path_lower = file_path.lower()
    if 'ncdiag' in path_lower:
        return 'ncdiag'
    elif 'odas' in path_lower:
        return 'odas'
    elif 'gdas' in path_lower:
        return 'gdas_marine'
    else:
        return 'unknown'


def register_observation(filename, file_path, parts, dry_run=True):
    """Register observation files using observation-specific parameters"""

    file_ext = parts[-1]
    provider = guess_provider_from_path(file_path)

    if len(parts) >= 6:
        obs_type = parts[-3]      # third from end (before timestamp and extension)
        timestamp = parts[-2]     # second from end (before extension)
        window_length = 'PT6H'    # default for all
    else:
        print(f"{file_path} can not be registered - not enough parts")
        return False

    print(f"\n{BLUE}{filename}{RESET}")
    print(f"   {YELLOW}OBSERVATION:{RESET} provider={provider}, obs_type={obs_type}, time={timestamp}")

    if dry_run:
        print(f"   {YELLOW}DRY RUN{RESET}")
        print(f"timestamp is {timestamp}")
        return True

    try:
        r2d2.store(
            item='observation',
            provider=provider,
            observation_type=obs_type,
            file_extension=file_ext,
            data_store='r2d2-experiments-nccs-gmao',
            window_start=timestamp,
            window_length=window_length,
            source_file=file_path
        )
        print(f"   {GREEN}SUCCESS{RESET}")
        save_registered(filename)
        return True
    except Exception as e:
        print(f"   {RED}ERROR:{RESET} {e}")
        return False

def register_background(filename, file_path, parts, dry_run=True):
    """Register background/forecast files using forecast specific parameters"""

    file_ext = parts[-1]

    # Guess model from filename/path
    name_lower = filename.lower()
    if 'mom6' in name_lower or 'ocean' in name_lower:
        model = 'mom6_cice6_UFS'
    elif 'cice' in name_lower or 'ice' in name_lower:
        model = 'mom6_cice6_UFS'
    else:
        model = 'geos'  # default

    # Extract timestamp - try different patterns
    timestamp = None
    for part in parts:
        # Look for YYYYMMDD pattern
        if len(part) == 8 and part.isdigit():
            year, month, day = part[:4], part[4:6], part[6:8]
            timestamp = f"{year}-{month}-{day}T12:00:00Z"
            break
        # Look for YYYYMMDDHH pattern
        elif len(part) == 10 and part.isdigit():
            year, month, day, hour = part[:4], part[4:6], part[6:8], part[8:10]
            timestamp = f"{year}-{month}-{day}T{hour}:00:00Z"
            break

    if not timestamp:
        timestamp = "2023-10-09T12:00:00Z"  # fallback

    print(f"\n{BLUE}{filename}{RESET}")
    print(f"   {YELLOW}BACKGROUND:{RESET} model={model}, time={timestamp}")

    if dry_run:
        print(f"   {YELLOW}DRY RUN{RESET}")
        return True

    try:
        r2d2.store(
            item='forecast',
            model='mom6', #model,
            experiment='s2s',  # Use this for testing
            file_extension='res', #file_ext,
            resolution='72x36', #C180
            step='P1DT12H',
            date=timestamp,
            file_type='MOM.res',
            source_file=file_path
        )
        print(f"   {GREEN}SUCCESS{RESET}")
        save_registered(filename)
        return True
    except Exception as e:
        print(f"   {RED}ERROR:{RESET} {e}")
        return False


def register_bias_correction(filename, file_path, parts, dry_run=True):
    """Register bias correction files"""
    
    file_ext = parts[-1]
    
    if len(parts) >= 6:
        obs_type = parts[-3]
        timestamp = parts[-2]
        window_length = 'PT6H'
    else:
        print(f"{file_path} can not be registered - not enough parts")
        return False

    print(f"\n{BLUE}{filename}{RESET}")
    print(f"   {YELLOW}BIAS CORRECTION:{RESET} obs_type={obs_type}, time={timestamp}")
    
    if dry_run:
        print(f"   {YELLOW}DRY RUN{RESET}")
        return True

    try:
        r2d2.store(
            item='bias_correction',
            provider='gsi',
            observation_type=obs_type,
            file_extension=file_ext,
            window_start=timestamp,
            window_length=window_length,
            source_file=file_path
        )
        print(f"   {GREEN}SUCCESS{RESET}")
        save_registered(filename)
        return True
    except Exception as e:
        print(f"   {RED}ERROR:{RESET} {e}")
        return False

def register_files(file_path, item_type, dry_run=True):
    """Register files found recursively from file_path"""
    
    # Load already registered files
    registered = load_registered()

    # If it's a file, just process that file
    if os.path.isfile(file_path) and file_path.endswith('.nc4'):
        files = [file_path]
    else:
        # If it's a directory, find all .nc4 and .txt files recursively
        if os.path.isdir(file_path):
            # find all nc4, nc , txt files
            files = glob.glob(os.path.join(file_path, "**/*.nc4"), recursive=True)
            files.extend(glob.glob(os.path.join(file_path, "**/*.txt"), recursive=True))
            files.extend(glob.glob(os.path.join(file_path, "**/*.nc"), recursive=True))
        else:
            print(f"❌ Path not found: {file_path}")
            return
    
    print(f"{YELLOW}Found {len(files)} files{RESET}")
    
    success_count = 0
    for file_path in files:
        filename = os.path.basename(file_path)
        
        # Check if already registered
        if filename in registered:
            print(f"{YELLOW}**** {filename} -  already registered{RESET}")
            continue

        # Split filename by "."
        parts = filename.split(".")
        
        if len(parts) < 4:
            print(f"{YELLOW}Skip {filename} - not enough parts{RESET}")
            continue
        
        # Call appropriate registration function based on item type
        if item_type == "observation":
            success = register_observation(filename, file_path, parts, dry_run)
        elif item_type in ["background", "forecast"]:
            success = register_background(filename, file_path, parts, dry_run)
        elif item_type in ["bias_coefficient", "bias_correction"]:
            success = register_bias_correction(filename, file_path, parts, dry_run)
        else:
            print(f"{RED}Unknown item type: {item_type}{RESET}")
            continue
            
        if success:
            success_count += 1

    print(f"\n{GREEN}Successfully processed {success_count}/{len(files)} files{RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Register files to r2d2 v3")
    parser.add_argument('path', help="File or directory path to register")
    parser.add_argument('item_type', help="Item type: observation, background, bias_correction")
    parser.add_argument('--register', action='store_true', help="Actually register (default is dry run)")
    
    args = parser.parse_args()
    
    dry_run = not args.register
    
    print(f"{YELLOW}{'DRY RUN' if dry_run else 'REGISTERING'} {args.item_type} files from: {args.path}{RESET}")
    register_files(args.path, args.item_type, dry_run=dry_run)
    
    if dry_run:
        print(f"\n{YELLOW}This was a DRY RUN. Use --register to actually register files{RESET}")

if __name__ == "__main__":
    main()
