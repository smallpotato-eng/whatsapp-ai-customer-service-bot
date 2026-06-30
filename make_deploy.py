import os, shutil, sys

src = r"${PROJECT_ROOT}\cs-ai"
dst = r"${USER_HOME}\Desktop\CS-AI-Deploy"

# Clean destination
if os.path.exists(dst):
    shutil.rmtree(dst)
os.makedirs(dst)

# Folders to copy (exclude node_modules, __pycache__, .db files)
def copy_folder(name, exclude_dirs=None, exclude_ext=None):
    exclude_dirs = exclude_dirs or []
    exclude_ext  = exclude_ext  or []
    src_path = os.path.join(src, name)
    dst_path = os.path.join(dst, name)
    if not os.path.exists(src_path):
        print(f"  SKIP (not found): {name}")
        return
    for root, dirs, files in os.walk(src_path):
        # Remove excluded dirs in-place
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        rel = os.path.relpath(root, src_path)
        target_dir = os.path.join(dst_path, rel)
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            if any(f.endswith(e) for e in exclude_ext):
                continue
            if f == 'nul':
                continue
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target_dir, f)
            shutil.copy2(src_file, dst_file)
    print(f"  OK: {name}")

print("Building CS-AI-Deploy...")
copy_folder("api",         exclude_dirs=["__pycache__"], exclude_ext=[".pyc"])
copy_folder("clients")
copy_folder("db",          exclude_ext=[".db"])
copy_folder("n8n-exports")
copy_folder("whatsapp",    exclude_dirs=["sessions"])

# Copy bat files
for f in ["install.bat", "start.bat", "check.bat"]:
    shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
    print(f"  OK: {f}")

# Create empty folders
os.makedirs(os.path.join(dst, "quotations"), exist_ok=True)
os.makedirs(os.path.join(dst, "db"), exist_ok=True)

# Fix CRLF on all .bat files (Write tool saves LF-only which breaks Windows CMD)
for root, dirs, files in os.walk(dst):
    for f in files:
        if f.endswith('.bat'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                data = fh.read()
            data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            with open(path, 'wb') as fh:
                fh.write(data)

# Count files
total = sum(len(files) for _, _, files in os.walk(dst))
print(f"\nDone! {total} files at: {dst}")
