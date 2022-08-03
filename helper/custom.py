import os
import shutil
import zipfile

def extract_jar(file_path:str, target_file:str) -> bool:
    file_dir = os.path.dirname(file_path)

    try:
        with zipfile.ZipFile(file_path, 'r') as zf, open(target_file, 'wb') as f:
            zfl = zf.infolist()
            for i in zfl:
                if i.filename.endswith('.jar'):
                    print(f"Extract file: {i.filename}")
                    shutil.copyfileobj(zf.open(i.filename), f)
    except Exception as e:
        print("Error occur during zip...")
        print(f"Error message:\n{e}")
        return False
    os.remove(file_path)
    return True

