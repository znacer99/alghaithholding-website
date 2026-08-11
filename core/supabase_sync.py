import os
import requests
from flask import current_app

def upload_file_to_supabase(supabase_url, supabase_key, bucket_name, local_path, storage_path):
    """Upload a file to Supabase Storage using raw PUT binary requests"""
    if not local_path or not os.path.exists(local_path):
        return None

    filename = os.path.basename(storage_path)
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{storage_path}"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "x-upsert": "true"
    }

    try:
        current_app.logger.info(f"Supabase Auto-Sync: Uploading {filename} to Storage...")
        with open(local_path, "rb") as f:
            file_data = f.read()

        # Send raw bytes via POST with x-upsert header
        res = requests.post(url, headers=headers, data=file_data)
        if res.status_code in [200, 201]:
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{storage_path}"
            current_app.logger.info(f"Supabase Auto-Sync: Successfully uploaded {filename}. URL: {public_url}")
            return public_url
        else:
            current_app.logger.error(f"Supabase Auto-Sync: Upload failed for {filename} ({res.status_code}): {res.text}")
            return None
    except Exception as e:
        current_app.logger.error(f"Supabase Auto-Sync: Exception during upload for {filename}: {e}")
        return None

def sync_candidate_to_supabase(candidate, cv_local_path, id_local_path):
    """Sync a candidate record to Supabase database & storage with fail-safe logging"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        current_app.logger.warning("Supabase Auto-Sync skipped: SUPABASE_URL or SUPABASE_KEY not configured in environment.")
        return False

    current_app.logger.info(f"Supabase Auto-Sync: Starting sync for candidate {candidate.full_name}...")

    # Upload files to storage first if local paths are provided
    new_cv_url = None
    if cv_local_path and os.path.exists(cv_local_path):
        filename = os.path.basename(cv_local_path)
        new_cv_url = upload_file_to_supabase(
            supabase_url, supabase_key, "candidates", cv_local_path, f"candidates/{filename}"
        )

    new_id_url = None
    if id_local_path and os.path.exists(id_local_path):
        filename = os.path.basename(id_local_path)
        new_id_url = upload_file_to_supabase(
            supabase_url, supabase_key, "candidates", id_local_path, f"candidates/{filename}"
        )

    # Standardize/Map Nationality for clean Supabase data before syncing
    nationality_cleaned = clean_nationality_value(candidate.nationality)

    # Fetch max ID from Supabase to assign unique primary key without overwriting existing data
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    target_id = None
    try:
        res_max = requests.get(f"{supabase_url}/rest/v1/candidates?select=id&order=id.desc&limit=1", headers=headers)
        if res_max.status_code == 200 and res_max.json():
            max_id = res_max.json()[0].get('id', 0)
            target_id = max_id + 1
            current_app.logger.info(f"Supabase Auto-Sync: Highest existing ID is {max_id}. Assigning new ID {target_id}.")
        else:
            target_id = candidate.id
    except Exception as e:
        current_app.logger.error(f"Supabase Auto-Sync: Error fetching max ID from Supabase: {e}")
        target_id = candidate.id

    # Build the database payload
    record = {
        "id": target_id,
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone,
        "nationality": nationality_cleaned,
        "applied_position": candidate.applied_position,
        "specialty": candidate.specialty,
        "experience": candidate.experience,
        "education": candidate.education,
        "skills": candidate.skills,
        "department_id": candidate.department_id,
        "cv_filepath": new_cv_url if new_cv_url else candidate.cv_filepath,
        "id_document_filepath": new_id_url if new_id_url else candidate.id_document_filepath,
        "status": candidate.status or "new"
    }

    # REST Postgrest upsert request
    url = f"{supabase_url}/rest/v1/candidates"
    headers["Prefer"] = "resolution=merge-duplicates"

    try:
        res = requests.post(url, headers=headers, json=record)
        if res.status_code in [200, 201]:
            current_app.logger.info(f"Supabase Auto-Sync: Successfully inserted/synced candidate {candidate.full_name} (Supabase ID: {target_id}) to Supabase Database.")
            return True
        else:
            current_app.logger.error(f"Supabase Auto-Sync: Database insert failed ({res.status_code}): {res.text} | Payload: {record}")
            return False
    except Exception as e:
        current_app.logger.error(f"Supabase Auto-Sync: Exception during DB sync for candidate {candidate.full_name}: {e}")
        return False

def clean_nationality_value(val):
    """Standardize nationality inputs for clean data integration"""
    if not val:
        return ""
    
    val_clean = str(val).strip().lower()
    
    # Algerian maps
    if any(k in val_clean for k in ["algeria", "algerian", "algerie", "algerien", "algerienne", "algerin", "algerina", "algéria", "algérie", "جزائر", "جزار"]):
        return "Algerian"
    
    # Tunisian maps
    if any(k in val_clean for k in ["tunis", "tunisian", "tunisie", "tunisienne", "tounis", "tounes", "تونس", "تونسي"]):
        return "Tunisian"
        
    # Indian maps
    if any(k in val_clean for k in ["india", "indian", "هند"]):
        return "Indian"
        
    # Syrian maps
    if any(k in val_clean for k in ["syria", "syrian", "سور"]):
        return "Syrian"
        
    # Egyptian maps
    if any(k in val_clean for k in ["egypt", "egyptian", "مصر"]):
        return "Egyptian"
        
    # Sudanese maps
    if any(k in val_clean for k in ["sudan", "sudanese", "سودان"]):
        return "Sudanese"
        
    # Libyan maps
    if any(k in val_clean for k in ["libya", "libyan", "ليب"]):
        return "Libyan"
        
    # Palestinian maps
    if any(k in val_clean for k in ["palestin", "فلس"]):
        return "Palestinian"
        
    # Kenyan maps
    if any(k in val_clean for k in ["kenya", "kenyan", "كين"]):
        return "Kenyan"

    # Ugandan maps
    if any(k in val_clean for k in ["uganda", "ugandan", "أوغ"]):
        return "Ugandan"
        
    # Return capitalized fallback
    return val.strip().capitalize()
