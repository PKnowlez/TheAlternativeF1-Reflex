import os
import mimetypes
import boto3

# Dynamic paths based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Search for credentials file in Reflex folder first
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "r2_credentials.env")
if not os.path.exists(CREDENTIALS_PATH):
    CREDENTIALS_PATH = r"c:\Users\pacma\OneDrive\Documents\Antigravity Coding\TheAlternativeF1-Cloudflare\r2_credentials.env"

# 2. Upload source directory
SOURCE_DIR = r"c:\Users\pacma\OneDrive\Documents\Antigravity Coding\TheAlternativeF1-Cloudflare"

def load_env_file(filepath):
    """Load and parse custom .env credentials file."""
    config = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Credentials file not found at {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                config[key] = val
    return config

def main():
    print(f"Loading credentials from: {CREDENTIALS_PATH}")
    try:
        creds = load_env_file(CREDENTIALS_PATH)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return

    # Extract credentials
    endpoint_url = creds.get("CLOUDFLARE_R2_ENDPOINT_URL")
    access_key = creds.get("CLOUDFLARE_R2_ACCESS_KEY_ID")
    secret_key = creds.get("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    bucket_name = creds.get("CLOUDFLARE_R2_BUCKET_NAME")

    # Validate
    missing = [k for k in ["CLOUDFLARE_R2_ENDPOINT_URL", "CLOUDFLARE_R2_ACCESS_KEY_ID", "CLOUDFLARE_R2_SECRET_ACCESS_KEY", "CLOUDFLARE_R2_BUCKET_NAME"] if not creds.get(k)]
    if missing:
        print(f"Error: Missing required keys in credentials file: {missing}")
        return

    print("Initializing R2 S3 Client...")
    try:
        s3 = boto3.client(
            service_name="s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto"
        )
    except Exception as e:
        print(f"Failed to initialize boto3 client: {e}")
        return

    # Fetch existing objects in the bucket to skip duplicates
    print("Checking R2 bucket for existing files...")
    existing_objects = {}
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Map: object_key -> file_size_in_bytes
                    existing_objects[obj['Key']] = obj['Size']
        print(f"Found {len(existing_objects)} objects already stored in R2.")
    except Exception as e:
        print(f"Warning: Could not list existing objects (bucket might be empty): {e}")

    print(f"Scanning directory: {SOURCE_DIR}")
    
    # Exclude credentials, instructions, and the script itself if it exists in the source folder
    exclude_files = {"r2_credentials.env", "cloudflare_r2_instructions.md", "upload_to_r2.py"}
    exclude_dirs = {".git", ".vscode", "__pycache__"}

    files_to_upload = []
    skipped_count = 0
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file in exclude_files or file.lower().endswith(".psd"):
                continue
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, SOURCE_DIR)
            s3_key = rel_path.replace(os.path.sep, "/")
            
            # Check if file already exists in R2 with exact same size
            local_size = os.path.getsize(full_path)
            if s3_key in existing_objects and existing_objects[s3_key] == local_size:
                skipped_count += 1
                continue
                
            files_to_upload.append((full_path, s3_key, local_size, s3_key in existing_objects))

    total_to_upload = len(files_to_upload)
    print(f"Total files in source: {total_to_upload + skipped_count}")
    print(f"Already uploaded (unchanged): {skipped_count}")
    print(f"To upload / update: {total_to_upload}")

    if total_to_upload == 0:
        print("\nAll files are already up to date!")
        return

    successful = 0
    failed = 0

    for idx, (local_path, r2_key, local_size, exists) in enumerate(files_to_upload, start=1):
        mime_type, _ = mimetypes.guess_type(local_path)
        extra_args = {}
        if mime_type:
            extra_args["ContentType"] = mime_type

        action_str = "Updating modified file" if exists else "Uploading new file"
        print(f"[{idx}/{total_to_upload}] {action_str}: {r2_key} ({mime_type or 'unknown type'})...")
        try:
            s3.upload_file(
                Filename=local_path,
                Bucket=bucket_name,
                Key=r2_key,
                ExtraArgs=extra_args
            )
            successful += 1
        except Exception as e:
            print(f"ERROR uploading {r2_key}: {e}")
            failed += 1

    print("\nUpload Complete!")
    print(f"Successfully processed: {successful}/{total_to_upload} files.")
    if failed > 0:
        print(f"Failed uploads: {failed} files.")

if __name__ == "__main__":
    main()
