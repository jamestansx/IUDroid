import hashlib
import json
import os
import pathlib
import shutil
import zipfile

from androguard.misc import AnalyzeAPK

def mkdir(directory) -> None:
    if directory:
        print(f"mkdir {directory}")
        os.makedirs(directory, exist_ok=True)

def mkdirs(directory_dict: dict) -> None:
    for d in directory_dict:
        if directory_dict[d]:
            print(f"mkdir {directory_dict[d]} ({d})")
            os.makedirs(directory_dict[d], exist_ok=True)

def check_sha256(file_path:str, shasum:str) -> bool:
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest() == shasum

def get_apk_info(index_file_path:str, apk_name:str) -> tuple:
    with open(index_file_path, 'r') as f:
        d = json.loads(f.read())["packages"][apk_name][0]
    return d["apkName"], d["hash"]

def install_lib(apk_file:str, dest_path: str) -> bool:
    with zipfile.ZipFile(apk_file, 'r') as zf:
        zfl = zf.infolist()
        lib_list = [f for f in zfl if "lib" in f.filename]

        #TODO: Enable using different arch(s)
        lib_list = [lib for lib in lib_list if 'arm64' in lib.filename]

        if not lib_list:
            return True

        for lib_info in lib_list:
            lib_path = lib_info.filename
            dest_dir = os.path.join(dest_path, os.path.dirname(lib_path).split('-')[0])
            install_path = os.path.join(dest_dir, lib_path.split('/')[-1])
            mkdir(dest_dir)

            with open(install_path, 'wb+') as fout, zf.open(lib_path) as fsrc:
                shutil.copyfileobj(fsrc, fout)
                if hashlib.sha256(fsrc.read()).hexdigest() == hashlib.sha256(fout.read()).hexdigest():
                    continue
                else:
                    return False
    return True

def create_privapp_permissions_whitelist(apk_file:str, xml_path:str) -> bool:
    a, _, _ = AnalyzeAPK(apk_file)

    mkdir(xml_path)
    xml_file = os.path.join(xml_path, a.get_package() + ".xml")

    with open(xml_file, 'w') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write("<permissions>\n")
        f.write(f'  <privapp-permissions package="{a.get_package()}">\n')
        for permission in a.permissions:
            f.write(f'      <permission name="{permission}" />\n')
            print(f"Writing permission: {permission}")
        f.write("   </privapp-permissions>\n")
        f.write("</permissions>")
    return True

def create_replace_list(replace_list:list, service_file:str) -> bool:
    with open(service_file, 'a') as f:
        f.write("\n")
        f.write("REPLACE=\"\n")
        for replace in replace_list:
            f.write(f"{replace}\n")
            print(f"Replacing: {replace}")
        f.write('"\n')
    return True

def zip_module(module_dir:str, dest_path:str) -> bool:
    directory = pathlib.Path(module_dir)
    try:
        with zipfile.ZipFile(dest_path, 'w') as archive:
            for f in directory.rglob('*'):
                print(f"Zipping file: {f}")
                archive.write(
                        f,
                        arcname=f.relative_to(directory)
                    )
    except Exception as e:
        print("Error occur during zip...")
        print(f"Error message:\n{e}")
        return False
    return True

def print_progress(stat:bool, message:str) -> None:
    status = "\u2713" if stat else "\u274C" 
    print(f"{message}: {status}")

def push_vercode(file_path:str, inc:int=1) -> bool:
    with open(file_path, 'r+') as f:
        content = f.read()
        content = content.split('\n')
        con_dict = dict()
        for i in content:
            if not i:
                continue

            i = i.split('=')
            con_dict[i[0]] = i[1]

        if not con_dict:
            print("Cannot update version code")
            return False

        ver = list(map(int,con_dict["version"][1:].split('.')))
        ver.reverse()

        for i,n in enumerate(ver):
            if i == len(ver) - 1:
                break
            if n >= 9:
                ver[i+1] += 1
                ver[i] = 0
                continue
            if i == 0:
                ver[i] += 1
            break
        
        ver.reverse()
        versioncode = '0'.join(map(str,ver))
        ver = f"v{'.'.join(map(str,ver))}"

        con_dict["version"] = ver
        con_dict["versionCode"] = versioncode

        print(con_dict)
        f.seek(0,0)
        for i in con_dict:
            f.write(f"{i}={con_dict[i]}\n")
