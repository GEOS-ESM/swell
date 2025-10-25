"""
Simple generic script to register observation files to r2d2 v3
Works for ncdiag, odas, gdas_marine, etc.
"""

import os
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
    raise ImportError(
        f"Failed to import r2d2: {e}\nLoad module: module load r2d2-client/sles15_0604"
    )

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
    print(f"   {YELLOW}OBSERVATION:{RESET} provider={provider}, \
            obs_type={obs_type}, time={timestamp}")

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
            # data_store='r2d2-experiments-nccs-gmao', # no need to specify, will be set by credentials
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
            model='mom6',  # model,
            experiment='s2s',  # Use this for testing
            file_extension='res',  # file_ext,
            resolution='72x36',  # C180
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

    # Parse filename: gsi.x0050.bc.aircraft_temperature.2023-10-09T15:00:00Z.acftbias
    # Parts would be: ['gsi', 'x0050', 'bc', 'aircraft_temperature', '2023-10-09T15:00:00Z', 'acftbias']

    if len(parts) < 6:
        print(f"{file_path} can not be registered - not enough parts")
        return False

    provider = parts[0]          # 'gsi'
    experiment = parts[1]        # 'x0050'
    obs_type = parts[3]          # 'aircraft_temperature'
    timestamp = parts[4]         # '2023-10-09T15:00:00Z'
    file_ext = parts[-1]         # 'acftbias'

    # Determine file_type from file_extension
    # Map file_extension -> file_type (R2D2 enum)
    # Using file extension as file_type since R2D2 instance accepts these
    # Following official JCSDA enums:
    #                      satbias, tlapse, obsbias_tlapse,
    #                      obsbias_coeff_errors, obsbias_coefficients

    file_ext_to_type = {
        # Aircraft bias corrections
        'acftbias': 'obsbias_coefficients',  # Aircraft bias coefficients
        'acftbias_cov': 'obsbias_coeff_errors',  # Aircraft bias coefficient errors

        # Satellite bias corrections
        'satbias': 'satbias',                                    # Special case: kept for GSI compatibility
        'satbias_cov': 'obsbias_coeff_errors',   # Coefficient errors (same as aircraft)

        # Timelapse
        'tlapse': 'obsbias_tlapse',
    }

    file_type = file_ext_to_type.get(file_ext, file_ext)

    # TODO: Add model determination
    # Determine model from observation type or path
    # Aircraft and most conventional obs - geos
    # Satellite radiances -> could be geos or gfs, default to geos
    # path_lower = file_path.lower()
    # if 'gfs' in path_lower:
    #     model = 'gfs'
    # elif 'fv3' in path_lower:
    #     model = 'fv3'
    # else:
    model = 'geos'  # default

    print(f"\n{BLUE}{filename}{RESET}")
    print(f"   {YELLOW}BIAS CORRECTION:{RESET}")
    print(f"      provider={provider}, experiment={experiment}")
    print(f"      model={model}, obs_type={obs_type}")
    print(f"      file_extension={file_ext}, file_type={file_type}")
    print(f"      date={timestamp}")

    if dry_run:
        print(f"   {YELLOW}DRY RUN{RESET}")
        return True

    try:
        r2d2.store(
            item='bias_correction',
            source_file=file_path,
            model=model,
            experiment=experiment,         # CRITICAL: experiment-specific
            provider=provider,             # From filename
            observation_type=obs_type,
            file_extension=file_ext,
            date=timestamp,
            file_type=file_type,           # Map extension to R2D2 enum
            # data_store='r2d2-experiments-nccs-gmao', # no need to specify, will be set by credentials
            # window_length='PT6H', # not required for bias correction
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

    # Define valid extensions based on item type
    valid_extensions = {
        'observation': ['.nc4', '.nc'],
        'bias_correction': ['.acftbias', '.satbias', '.tlapse', '.acftbias_cov', '.satbias_cov'],
        'background': ['.nc4', '.nc', '.res'],
        'forecast': ['.nc4', '.nc', '.res']
    }

    extensions = valid_extensions.get(item_type, ['.nc4', '.nc'])

    # If it's a file, just process that file
    if os.path.isfile(file_path):
        # Check if file has valid extension for this item type
        if any(file_path.endswith(ext) for ext in extensions):
            # If it has a valid extension, process it
            files = [file_path]
        else:
            print(f"{RED}File {file_path} doesn't have a valid extension for {item_type}{RESET}")
            print(f"{YELLOW}Valid extensions: {', '.join(extensions)}{RESET}")
            return
    else:
        # If it's a directory, find all matching files recursively
        if os.path.isdir(file_path):
            files = []

            for ext in extensions:
                files.extend(glob.glob(os.path.join(file_path, "**/*" + ext), recursive=True))
        else:
            print(f"{RED}Path not found: {file_path} {RESET}")
            return

    print(f"{YELLOW}Found {len(files)} files{RESET}")

    success_count = 0
    failed_files = []
    skipped_files = []

    for file_path in files:
        filename = os.path.basename(file_path)

        # Check if already registered
        if filename in registered:
            print(f"{YELLOW}**** {filename} -  already registered{RESET}")
            skipped_files.append(filename)
            continue

        # Split filename by "."
        parts = filename.split(".")

        if len(parts) < 4:
            print(f"{YELLOW}Skip {filename} - not enough parts{RESET}")
            skipped_files.append(filename)
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
            failed_files.append((filename, "Unknown item type"))
            continue

        if success:
            success_count += 1
        else:
            failed_files.append((filename, "Registration failed"))

    # Print summary
    print(f"\n{GREEN}Successfully processed {success_count}/{len(files)} files{RESET}")

    if skipped_files:
        print(f"{YELLOW}Skipped {len(skipped_files)} files (already registered or invalid format){RESET}")

    if failed_files:
        print(f"\n{RED}Failed to register {len(failed_files)} file(s):{RESET}")
        for filename, reason in failed_files:
            print(f"  {RED}{RESET} {filename}: {reason}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Register files to r2d2 v3")
    parser.add_argument('path', help="File or directory path to register")
    parser.add_argument('item_type', help="Item type: observation, background, bias_correction")
    parser.add_argument(
        '--register',
        action='store_true',
        help="Actually register (default is dry run)")

    args = parser.parse_args()

    dry_run = not args.register

    print(f"{YELLOW}{'DRY RUN' if dry_run else 'REGISTERING'} {args.item_type} files from: "
          f"{args.path}{RESET}")
    register_files(args.path, args.item_type, dry_run=dry_run)

    if dry_run:
        print(f"\n{YELLOW}This was a DRY RUN. Use --register to actually register files{RESET}")


if __name__ == "__main__":
    main()
