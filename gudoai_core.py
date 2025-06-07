# gudoai_core.py
import os
import json
import uuid
import subprocess
from gudoai_api_client import GudoaiApiClient  # Modul untuk berinteraksi dengan API simulasi

class GudoaiCore:
    def __init__(self):
        """Tahapan 3: Inisialisasi objek GudoaiCore.
        
        - Membuat klien API untuk interaksi dengan server simulasi.
        """
        self.api_client = GudoaiApiClient()

    def init_project(self, project_name):
        """Tahapan 1: Fungsi untuk membuat proyek baru.
        
        - Membuat direktori dengan nama <project_name>.
        - Menginisialisasi Git di dalamnya.
        - Membuat file metadata gudoai_meta.json.
        - Melakukan commit awal ke Git.
        """
        if os.path.exists(project_name):
            raise FileExistsError(f"Project '{project_name}' already exists.")
        os.makedirs(project_name)
        print(f"Created directory: {project_name}")
        self._create_gudoai_meta(project_name)      # Membuat file metadata
        self._init_git_repo(project_name)          # Inisialisasi repositori Git
        self._git_initial_commit(project_name)     # Commit awal

    def _create_gudoai_meta(self, project_name):
        """Tahapan 1: Membuat file gudoai_meta.json sebagai metadata proyek.
        
        - File ini menyimpan informasi seperti:
          * project_id: UUID unik.
          * version: Angka mulai dari 0.
          * description: Deskripsi default.
          * last_api_sync_commit_hash: Hash commit terakhir dari API (belum sync).
          * api_registered: Status proyek belum terdaftar di API.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        meta = {
            "project_id": str(uuid.uuid4()),              # UUID unik untuk proyek
            "version": 0,                                 # Mulai dari versi 0
            "description": "New GUDOAI managed project.",   # Deskripsi default
            "last_api_sync_commit_hash": None,              # Belum pernah sync dengan API
            "api_registered": False                         # Belum terdaftar di API
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)  # Simpan data ke file JSON
        print(f"Created metadata file in: {meta_path}")

    def _init_git_repo(self, project_name):
        """Tahapan 1 & 5: Menginisialisasi repositori Git.
        
        - Ini adalah langkah pertama dalam pembuatan proyek.
        - Jika gagal, error akan dilemparkan.
        """
        result = subprocess.run(
            ['git', 'init'],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git init failed: {result.stderr}")
        print("Initialized Git repository")

    def _git_initial_commit(self, project_name):
        """Tahapan 1 & 5: Melakukan commit awal untuk file gudoai_meta.json.
        
        - Ini adalah commit pertama setelah proyek dibuat.
        - Git digunakan untuk version control.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        subprocess.run(['git', 'add', 'gudoai_meta.json'], cwd=project_name, check=True)
        subprocess.run(['git', 'commit', '-m', 'GUDOAI: Initial project setup'], cwd=project_name, check=True)
        print("Performed initial Git commit")

    def update_metadata(self, project_name, new_description):
        """Tahapan 1: Memperbarui deskripsi dan meningkatkan versi.
        
        - Baca file gudoai_meta.json.
        - Update deskripsi dan tingkatkan versi.
        - Simpan perubahan.
        - Lakukan commit otomatis ke Git.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        with open(meta_path, 'r') as f:
            try:
                meta = json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"File {meta_path} is not valid JSON.")
        meta['description'] = new_description
        meta['version'] += 1
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        subprocess.run(['git', 'add', 'gudoai_meta.json'], cwd=project_name, check=True)
        commit_message = f"GUDOAI: Updated metadata - version {meta['version']}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=project_name, check=True)
        print(f"Metadata for '{project_name}' updated. Version: {meta['version']}")

    def create_feature_branch(self, project_name, branch_name):
        """Tahapan 1: Membuat dan beralih ke branch baru.
        
        - Branch baru memiliki format `feature/<branch_name>`.
        - Jika gagal, error akan muncul.
        """
        branch_name = f"feature/{branch_name}"  # Format branch sesuai konvensi Git
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create branch '{branch_name}': {result.stderr}")
        print(f"Created and switched to branch: {branch_name}")

    def merge_to_main(self, project_name, feature_branch_name):
        """Tahapan 1 & 5: Menggabungkan branch feature ke main.
        
        - Jika ada konflik, tidak lanjutkan commit.
        - Jika berhasil, lakukan commit.
        """
        feature_branch = f"feature/{feature_branch_name}"
        result = subprocess.run(
            ['git', 'checkout', 'master'],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to switch to main branch: {result.stderr}")
        result = subprocess.run(
            ['git', 'merge', feature_branch],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("⚠️ Konflik ditemukan. Merge tidak dilanjutkan.")
            return False
        print(f"Branch '{feature_branch}' berhasil digabungkan ke main.")
        return True

    def register_project(self, project_name):
        """Tahapan 2 & 3: Mendaftarkan proyek ke API simulasi.
        
        - Baca file gudoai_meta.json.
        - Jika sudah terdaftar, error.
        - Dapatkan hash commit terbaru.
        - Kirim data ke API via POST /v1/projects.
        - Jika sukses, perbarui metadata dan lakukan commit.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to read metadata: {e}")
        if meta.get("api_registered", False):
            raise ValueError("Project already registered with the API.")
        commit_hash = self._get_current_commit_hash(project_name)
        status_code, response = self.api_client.register_project(
            meta["project_id"],
            project_name,
            commit_hash,
            meta["version"],
            meta["description"]
        )
        if status_code == 201:
            meta["api_registered"] = True
            meta["last_api_sync_commit_hash"] = commit_hash
            meta["version"] += 1  # Tambahkan versi setelah registrasi
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            subprocess.run(['git', 'add', 'gudoai_meta.json'], cwd=project_name, check=True)
            subprocess.run(['git', 'commit', '-m', 'GUDOAI: Project registered to API'], cwd=project_name, check=True)
            print("✅ Project successfully registered with the API.")
        else:
            print(f"❌ Failed to register project: {response.get('error', 'Unknown error')}")

    def sync_project(self, project_name):
        """Tahapan 2 & 3: Menyinkronkan proyek dengan API simulasi.
        
        - Baca file gudoai_meta.json.
        - Jika belum terdaftar, error.
        - Dapatkan hash commit dan daftar file yang dilacak.
        - Kirim ke API via PUT /v1/projects/{project_id}/sync.
        - Jika sukses, perbarui metadata dan lakukan commit.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to read metadata: {e}")
        if not meta.get("api_registered", False):
            raise ValueError("Project not registered with the API.")
        commit_hash = self._get_current_commit_hash(project_name)
        files = self._get_tracked_files(project_name)
        status_code, response = self.api_client.sync_project(
            meta["project_id"],
            commit_hash,
            meta["version"],
            meta["description"],
            files
        )
        if status_code == 200:
            meta["last_api_sync_commit_hash"] = commit_hash
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            subprocess.run(['git', 'add', 'gudoai_meta.json'], cwd=project_name, check=True)
            subprocess.run(['git', 'commit', '-m', 'GUDOAI: Project synced with API'], cwd=project_name, check=True)
            print("✅ Project state synchronized with API.")
        else:
            print(f"❌ Failed to sync project: {response.get('error', 'Unknown error')}")

    def _get_current_commit_hash(self, project_name):
        """Tahapan 5: Mendapatkan hash commit terbaru dari branch utama."""
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get commit hash: {result.stderr}")
        return result.stdout.strip()

    def _get_tracked_files(self, project_name):
        """Tahapan 2 & 5: Mendapatkan daftar file yang sudah dilacak oleh Git."""
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get tracked files: {result.stderr}")
        return result.stdout.strip().split('\n')  # Kembalikan list file yang dilacak

    def check_api_status(self, project_name):
        """Tahapan 2 & 3: Mengecek status proyek dari API simulasi.
        - Ambil project_id dari file gudoai_meta.json.
        - Panggil GET /v1/projects/{project_id}/status.
        - Tampilkan informasi dari API.
        - Bandingkan hash commit lokal dengan API.
        """
        meta_path = os.path.join(project_name, "gudoai_meta.json")
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to read metadata: {e}")
        project_id = meta["project_id"]
        status_code, response = self.api_client.get_project_status(project_id)
        if status_code == 200:
            print(f"Status proyek '{project_name}':")
            print(f"  - Project ID: {response['project_id']}")
            print(f"  - Nama: {response['project_name']}")
            last_commit = response.get("last_synced_commit", "N/A")
            print(f"  - Last Synced Commit: {last_commit}")
            print(f"  - Metadata Version: {response.get('version', 'N/A')}")
            print(f"  - Deskripsi: {response['description']}")
            print(f"  - Is Deployed: {response.get('is_deployed', False)}")
            local_hash = meta.get("last_api_sync_commit_hash")
            if local_hash == last_commit:
                print("✅ Hash commit sama antara lokal dan API.")
            else:
                print("⚠️ Hash commit berbeda antara lokal dan API.")
        else:
            print(f"❌ Failed to get project status: {response.get('error', 'Unknown error')}")