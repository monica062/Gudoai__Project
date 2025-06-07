# gudoai_api_client.py
import json
import os

class GudoaiApiClient:
    def __init__(self):
        """Tahapan 2 & 3: Inisialisasi klien API simulasi.
        
        - Membaca database dari file .gudoai_api_db.json.
        - Jika file tidak ada, buat database kosong.
        """
        self.db_file = '.gudoai_api_db.json'
        self.projects = self._load_projects()

    def _load_projects(self):
        """Tahapan 2 & 3: Memuat data proyek dari file JSON."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load projects database: {e}")
                return {}
        else:
            return {}

    def _save_projects(self):
        """Tahapan 2 & 3: Menyimpan data proyek ke file JSON."""
        with open(self.db_file, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def register_project(self, project_id, project_name, commit_hash, version, description):
        """Tahapan 2 & 3: Mendaftarkan proyek ke API simulasi.
        
        - Jika project_id sudah ada, kembalikan error 409.
        - Jika belum ada, tambahkan ke database dan kembalikan respons 201.
        """
        if project_id in self.projects:
            return 409, {"error": "Project ID already registered"}
        self.projects[project_id] = {
            "project_id": project_id,
            "project_name": project_name,
            "commit_hash": commit_hash,
            "version": version,
            "description": description,
            "file_manifest": [],
            "last_synced_commit": None,
            "is_deployed": False
        }
        self._save_projects()
        return 201, {"message": "Project registered", "registry_id": project_id}

    def sync_project(self, project_id, commit_hash, version, description, file_manifest):
        """Tahapan 2 & 3: Menyinkronkan proyek dengan API simulasi.
        
        - Jika proyek tidak ada, kembalikan error 404.
        - Jika versi tidak valid, kembalikan error 400.
        - Jika berhasil, perbarui data dan kembalikan respons 200.
        """
        if project_id not in self.projects:
            return 404, {"error": "Project not found"}
        if version <= self.projects[project_id]["version"]:
            return 400, {"error": "Stale data: metadata_version must be greater than current."}
        self.projects[project_id].update({
            "commit_hash": commit_hash,
            "version": version,
            "description": description,
            "file_manifest": file_manifest,
            "last_synced_commit": commit_hash
        })
        self._save_projects()
        return 200, {"message": "Project state synchronized", "last_synced_commit": commit_hash}

    def get_project_status(self, project_id):
        """Tahapan 2 & 3: Mengecek status proyek dari API simulasi.
        
        - Jika proyek tidak ada, kembalikan error 404.
        - Jika ada, kembalikan data proyek.
        """
        if project_id not in self.projects:
            return 404, {"error": "Project not found"}
        return 200, self.projects[project_id]