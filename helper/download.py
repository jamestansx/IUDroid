import json
import os
import urllib.error
import urllib.request
import zipfile

from helper.common import *
from helper.parser import *


def download(download_url: str, dest_path: str) -> bool:
    try:
        print(f"downloading from: {download_url}")
        with urllib.request.urlopen(download_url) as response, open(
            dest_path, "wb"
        ) as out_file:
            shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError:
        print(f"HTTP Error: {download_url}")
        return False
    return True


def download_index(repo_name: str, repo_url: str, dest_dir: str) -> bool:
    jar_file = os.path.join(dest_dir, f"{repo_name}.jar")
    json_file = os.path.join(dest_dir, f"{repo_name}.json")
    repo_url += "/index-v1.jar"

    mkdir(dest_dir)

    if download(repo_url, jar_file):
        with zipfile.ZipFile(jar_file, "r") as zf, open(json_file, "w") as f:
            zfl = zf.infolist()
            for i in zfl:
                if i.filename.endswith(".json"):
                    print(f"Found: {i.filename}")
                    content = json.loads(zf.read(i.filename).decode())
                    f.write(json.dumps(content, indent=4))
    os.remove(jar_file)
    return True


def download_custom(
    download_type: str, raw_info: str, filename: str, dest_dir: str
) -> bool:
    if download_type != "github":
        print(f"{download_type} is not supported yet")
        return False

    github_raw_domain = "raw.githubusercontent.com"
    repo_branch = "master"
    dest_path = os.path.join(dest_dir, filename)
    repo_info, url_path = raw_info.split(":")
    download_url = f"https://{github_raw_domain}/{repo_info}/{repo_branch}/{url_path}"
    return download(download_url, dest_path)


def download_app_repo(
    filename: str, repo_name: str, apk_name: str, dest_dir: str, config
) -> bool:
    dest_dir = os.path.join(dest_dir, filename)
    mkdir(dest_dir)
    repo_index_path = os.path.join(
        config.get("Paths", "repo"),
        f"{repo_name}.json",
    )
    apk_name, shasum = get_apk_info(repo_index_path, apk_name)
    repo_url = config.get("Repos", repo_name)
    repo_url += "/" if repo_url[-1] != "/" else ""
    download_url = f"{repo_url}{apk_name}"
    dest_path = os.path.join(dest_dir, f"{filename}.apk")

    if download(download_url, dest_path) and check_sha256(dest_path, shasum):
        return install_lib(dest_path, dest_dir)
    return False


def download_app_git(
    filename: str, git_type: str, raw_info: str, dest_dir: str, release_type: str
) -> bool:
    dest_dir = os.path.join(dest_dir, filename)
    mkdir(dest_dir)
    repo_info, app_type = raw_info.split(":")

    if git_type.lower() == "github":
        download_url = parse_github_release_url(repo_info, app_type, release_type)

    if git_type.lower() == "gitlab":
        ver_tag = parse_gitlab_latest_tag(repo_info)
        download_url = parse_gitlab_release_url(repo_info, ver_tag, app_type)

    dest_path = os.path.join(dest_dir, f"{filename}.{app_type}")

    is_downloaded = download(download_url, dest_path)

    if is_downloaded and app_type == "apk":
        return install_lib(dest_path, dest_dir)
    return is_downloaded


def download_app(
    filename: str, download_type: str, raw_info: str, dest_dir: str, choice
) -> bool:
    if download_type.lower() in ["github", "gitlab"]:
        return download_app_git(filename, download_type, raw_info, dest_dir, choice)
    return download_app_repo(filename, download_type, raw_info, dest_dir, choice)


def download_framework(
        filename: str, git_type: str, raw_info: str, target_file: str, dest_dir: str, release_type: str
):
    if download_app_git(filename, git_type, raw_info, dest_dir, release_type):
        _, app_type = raw_info.split(":")
        target_file = os.path.join(dest_dir, target_file)
        dest_dir = os.path.join(dest_dir, filename)
        file_path = os.path.join(dest_dir, f"{filename}.{app_type}")
        os.rmdir(os.path.dirname(file_path))
        return extract_jar(file_path, target_file)
