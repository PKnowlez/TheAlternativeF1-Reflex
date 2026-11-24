import argparse
import os
import boto3

# Dynamic paths based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Search for credentials file in script folder first
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "r2_credentials.env")
if not os.path.exists(CREDENTIALS_PATH):
    CREDENTIALS_PATH = r"c:\Users\pacma\OneDrive\Documents\Antigravity Coding\TheAlternativeF1-Cloudflare\r2_credentials.env"

# 2. Download target directory
TARGET_DIR = r"c:\Users\pacma\OneDrive\Documents\Antigravity Coding\TheAlternativeF1-Cloudflare"

EXCLUDE_FILES = {
    "r2_credentials.env",
    "cloudflare_r2_instructions.md",
    "upload_to_r2.py",
    "download_from_r2.py",
}


def load_env_file(filepath):
    """Load and parse custom .env credentials file."""
    config = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Credentials file not found at {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                config[key] = val
    return config


def create_r2_client(creds):
    """Validate credentials and initialize the Cloudflare R2 S3 client."""
    required = [
        "CLOUDFLARE_R2_ENDPOINT_URL",
        "CLOUDFLARE_R2_ACCESS_KEY_ID",
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
        "CLOUDFLARE_R2_BUCKET_NAME",
    ]
    missing = [k for k in required if not creds.get(k)]
    if missing:
        raise ValueError(f"Missing required keys in credentials file: {missing}")

    return boto3.client(
        service_name="s3",
        endpoint_url=creds["CLOUDFLARE_R2_ENDPOINT_URL"],
        aws_access_key_id=creds["CLOUDFLARE_R2_ACCESS_KEY_ID"],
        aws_secret_access_key=creds["CLOUDFLARE_R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )


def resolve_local_path(r2_key, target_root):
    """Map an R2 object key to a safe, normalized local path inside target_root."""
    if not r2_key or r2_key.endswith("/"):
        return None

    parts = [p for p in r2_key.lstrip("/").replace("\\", "/").split("/") if p]
    if not parts or any(p in (".", "..") for p in parts):
        return None

    if parts[-1] in EXCLUDE_FILES:
        return None

    abs_target_root = os.path.abspath(target_root)
    local_path = os.path.abspath(os.path.join(abs_target_root, *parts))
    if os.path.commonpath([abs_target_root, local_path]) != abs_target_root:
        return None

    return local_path


def collect_r2_objects(s3, bucket_name, target_root):
    """List R2 objects and deduplicate case-insensitive Windows path collisions."""
    paginator = s3.get_paginator("list_objects_v2")
    deduped = {}
    ignored_count = 0

    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            r2_key = obj["Key"]
            local_path = resolve_local_path(r2_key, target_root)
            if local_path is None:
                ignored_count += 1
                continue

            norm_key = local_path.lower()
            existing = deduped.get(norm_key)
            if existing is not None:
                # Keep the most recently modified object if R2 has case-only duplicates
                if obj["LastModified"] <= existing["last_modified"]:
                    print(f"Warning: Skipping case-collision key '{r2_key}' (older than '{existing['key']}').")
                    continue
                print(f"Warning: Replacing case-collision key '{existing['key']}' with newer '{r2_key}'.")

            deduped[norm_key] = {
                "key": r2_key,
                "size": obj["Size"],
                "last_modified": obj["LastModified"],
                "local_path": local_path,
            }

    return list(deduped.values()), ignored_count


def main():
    parser = argparse.ArgumentParser(
        description="Sync files from Cloudflare R2 down to the local TheAlternativeF1-Cloudflare directory."
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview downloads without writing files.")
    parser.add_argument("--force", action="store_true", help="Re-download files even if local size matches R2.")
    args = parser.parse_args()

    print(f"Loading credentials from: {CREDENTIALS_PATH}")
    try:
        creds = load_env_file(CREDENTIALS_PATH)
        s3 = create_r2_client(creds)
    except Exception as e:
        print(f"Error initializing R2 client: {e}")
        return

    bucket_name = creds["CLOUDFLARE_R2_BUCKET_NAME"]

    print("Listing objects in R2 bucket...")
    try:
        r2_objects, ignored_count = collect_r2_objects(s3, bucket_name, TARGET_DIR)
    except Exception as e:
        print(f"Error listing R2 bucket: {e}")
        return

    print(f"Found {len(r2_objects)} syncable objects in R2 (ignored {ignored_count} markers/excluded entries).")
    print(f"Target directory: {TARGET_DIR}")

    files_to_download = []
    skipped_count = 0

    for item in sorted(r2_objects, key=lambda x: x["key"].lower()):
        local_path = item["local_path"]
        r2_size = item["size"]
        exists_locally = os.path.exists(local_path)

        if not args.force and exists_locally and os.path.getsize(local_path) == r2_size:
            skipped_count += 1
            continue

        files_to_download.append((item["key"], local_path, r2_size, exists_locally))

    total_to_download = len(files_to_download)
    print(f"Already in sync (unchanged): {skipped_count}")
    print(f"To download / update: {total_to_download}")

    if total_to_download == 0:
        print("\nLocal directory is already up to date!")
        return

    if args.dry_run:
        for idx, (r2_key, local_path, r2_size, exists_locally) in enumerate(files_to_download, start=1):
            action_str = "Would update" if exists_locally else "Would download"
            print(f"[{idx}/{total_to_download}] {action_str}: {r2_key} ({r2_size} bytes) -> {local_path}")
        print("\nDry run complete. No files were modified.")
        return

    successful = 0
    failed = 0

    for idx, (r2_key, local_path, r2_size, exists_locally) in enumerate(files_to_download, start=1):
        action_str = "Updating modified file" if exists_locally else "Downloading new file"
        print(f"[{idx}/{total_to_download}] {action_str}: {r2_key} ({r2_size} bytes)...")
        tmp_path = f"{local_path}.tmp"
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(Bucket=bucket_name, Key=r2_key, Filename=tmp_path)
            os.replace(tmp_path, local_path)
            successful += 1
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            print(f"ERROR downloading {r2_key}: {e}")
            failed += 1

    print("\nSync Complete!")
    print(f"Successfully processed: {successful}/{total_to_download} files.")
    if failed > 0:
        print(f"Failed downloads: {failed} files.")


if __name__ == "__main__":
    main()
