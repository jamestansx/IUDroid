import json
import os
import urllib.error
import urllib.request
import zipfile

from helper.common import *
from helper.parser import *


def download(download_url:str, dest_path:str) -> bool:
    try:
        print(f"downloading from: {download_url}")
        with urllib.request.urlopen(download_url) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError:
        print(f"HTTP Error: {download_url}")
        return False
    return True

def download_index(repo_name:str, repo_url:str, dest_dir:str) -> bool:
    jar_file = os.path.join(dest_dir, f"{repo_name}.jar")
    json_file = os.path.join(dest_dir, f"{repo_name}.json")
    repo_url += "/index-v1.jar"

    mkdir(dest_dir)

    if download(repo_url, jar_file):
        with zipfile.ZipFile(jar_file, 'r') as zf, open(json_file, 'w') as f:
            zfl = zf.infolist()
            for i in zfl:
                if i.filename.endswith('.json'):
                    print(f"Found: {i.filename}")
                    content = json.loads(zf.read(i.filename).decode())
                    f.write(json.dumps(content, indent=4))
    os.remove(jar_file)
    return True

def download_app(filename:str, download_type:str, raw_info:str, dest_dir:str, config=None) -> bool:
    download_url = str()
    app_type = "apk"
    dest_dir = os.path.join(dest_dir, filename)
    mkdir(dest_dir)
    shasum = None

    if download_type.lower() == "github":
        repo_info, app_type = raw_info.split(':')
        download_url = parse_github_latest_release_url(repo_info, app_type)
    elif download_type.lower() == "gitlab":
        repo_info, app_type = raw_info.split(':')
        ver_tag = parse_gitlab_latest_tag(repo_info)
        download_url = parse_gitlab_release_url(repo_info, ver_tag, app_type)
    else:
        repo_index_path = os.path.join(
                    config.get("Paths", "repo"), 
                    f"{download_type}.json",
                )
        apk_name, shasum = get_apk_info(repo_index_path, raw_info)
        repo_url = config.get("Repos", download_type)
        repo_url += "/" if repo_url[-1] != '/' else ''
        download_url = f"{repo_url}{apk_name}"

    dest_path = os.path.join(dest_dir, f"{filename}.{app_type}")

    if download(download_url, dest_path) and shasum is not None and not check_sha256(dest_path, shasum):
        return False

    return install_lib(dest_path, dest_dir)
    
def download_custom(download_type: str, raw_info:str, filename:str, dest_dir:str) -> bool:
    download_url = str()
    dest_path = os.path.join(dest_dir, filename)

    if download_type.lower() == "github":
        repo_info, app_type = raw_info.split(':')
        download_url = parse_github_latest_release_url(repo_info, app_type)
    elif download_type.lower() == "ghfile":
        repo_info, file_path = raw_info.split(':')
        github_raw_domain = "raw.githubusercontent.com"
        repo_branch = "master"
        download_url = f"https://{github_raw_domain}/{repo_info}/{repo_branch}/{file_path}"
    else:
        print(f"{download_type} is not supported yet")
        return False

    return download(download_url, dest_path)
