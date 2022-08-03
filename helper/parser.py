import json
import os
import urllib.request

gitlab_url = "https://gitlab.com/"
github_api_url = "https://api.github.com/repos/"

def parse_replace(section:dict) -> list:
    tmp_list = list()
    for basename in section:
        path = section[basename]
        if path[-1] != '/':
            path += '/'
        tmp_list.append(os.path.join(path, basename))
    return tmp_list

def parse_tools(tools_dict:dict) -> dict:
    tmp_dict = dict()
    for tool, info in tools_dict.items():
        tmp_dict[tool] = info.split(':')
    return tmp_dict

def parse_apps(apps_dict:dict) -> dict:
    tmp_dict = dict()
    for app, info in apps_dict.items():
        l = info.split(':')
        tmp_dict[app] = dict(name=l[0], repo=l[1], path=l[2])
    return tmp_dict 

def parse_app_type(info:str) -> tuple:
    return tuple(info.split(':'))

def parse_gitlab_latest_tag(repo_info:str) -> str:
    url = f"{gitlab_url}{repo_info}/-/tags"
    target = "ref-name"
    with urllib.request.urlopen(url) as response:
        res = response.read().decode()
        tag = res[res.find(target) + len(target):]
        tag = tag[tag.index('>') + 1:]
        tag = tag[:tag.index('<')]
    return tag

def parse_gitlab_release_url(repo_info:str, ver_tag: str, app_type:str) -> str:
    # This is a workaround to detect specific release from repo
    #TODO: Parse the html properly to detect the required url (apk or others)
    tag_url = f"{gitlab_url}{repo_info}/-/tags/{ver_tag}"
    target = 'data-canonical-src="'
    with urllib.request.urlopen(tag_url) as r:
        res = r.read().decode()
        while res.find(target) != -1:
            res = res[res.find(target) + len(target):]
            url = res[:res.find('"')]
            if url.split('.')[-1] == app_type:
                break
        return f"{gitlab_url}{repo_info}{url}"

def parse_github_latest_release_url(repo_info:str, app_type:str) -> str:
    api_url = f"{github_api_url}{repo_info}/releases/latest"

    with urllib.request.urlopen(api_url) as response:
        res_json = json.loads(response.read().decode())
        for release in res_json["assets"]:
            if release['name'].split('.')[-1] != app_type:
                continue
            return release['browser_download_url']
            

