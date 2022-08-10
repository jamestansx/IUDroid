#!/usr/bin/env python3

import argparse
import asyncio
import time
import shutil
import sys

from distutils.dir_util import copy_tree

from helper.common import *
from helper.config import *
from helper.download import *


def setup(file_path: str) -> configparser.ConfigParser:
    config = read_ini(file_path)
    mkdirs(config["Paths"])
    return config


async def main(args):
    start = time.perf_counter()
    config = setup(args.config)

    if args.delete:
        for i in ["module", "repo", "release"]:
            d = config.get("Paths", i)
            print(f"Deleting {d}")
            shutil.rmtree(d)

    if args.push_ver:
        module_file = "module.prop"
        push_vercode(os.path.join("src", module_file))

    if args.build:
        copy_tree("src", config.get("Paths", "module"))

    if args.update_indices or args.build:
        async_list = []
        for repo in config["Repos"]:
            print(f"* Updating {repo}")
            async_list.append(
                download_index(
                    repo, config.get("Repos", repo), config.get("Paths", "repo")
                )
            )
        await asyncio.gather(*async_list)

    if args.download_apps or args.build:
        async_list = []
        for appr in config["Apps_Repo"]:
            print(f"* Downloading {appr}")
            async_list.append(
                download_app(appr, *config.get("Apps_Repo", appr).split(";"), config)
            )

        for appg in config["Apps_Git"]:
            print(f"* Downloading {appg}")
            async_list.append(
                download_app(appg, *config.get("Apps_Git", appg).split(";"))
            )

        for framework in config["Framework"]:
            print(f"* Downloading {framework}")
            async_list.append(
                download_framework(
                    framework, *config.get("Framework", framework).split(";")
                )
            )

        for custom in config["Custom"]:
            print(f"* Downloading {custom}")
            param = config.get("Custom", custom).split(";")
            async_list.append(download_custom(*param))

        await asyncio.gather(*async_list)

    if args.write_perm or args.build:
        privapp_dir = pathlib.Path(config.get("Paths", "privapp"))
        for file in privapp_dir.rglob("*"):
            if file.is_file() and str(file).split(".")[-1] == "apk":
                print(f"* Writing priv-app permission {file}")
                print_progress(
                    create_privapp_permissions_whitelist(
                        file,
                        config.get("Paths", "permissions"),
                    ),
                    f"Priv-app Permission {file}",
                )

    if args.write_replace_list or args.build:
        print(f"* Writing replace list to customize.sh")
        print_progress(
            create_replace_list(
                parse_replace(config["Replace"]),
                os.path.join(config.get("Paths", "module"), "customize.sh"),
            ),
            f"Write replace list",
        )

    if args.zip or args.build:
        print(f"* Zipping Magisk module")
        print_progress(
            zip_module(
                config.get("Paths", "module"),
                os.path.join(config.get("Paths", "release"), "IUDroid.zip"),
            ),
            f"Zip module",
        )

    duration = time.perf_counter() - start
    print(f"--------{duration} seconds--------")
    print("Exiting...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        nargs="?",
        default="config.ini",
        help="Provide configuration ini file path [config.ini]",
    )
    parser.add_argument(
        "--update-indices",
        "-U",
        action="store_true",
        help="Update ALL repo indices",
    )
    parser.add_argument(
        "--download-apps",
        "-A",
        action="store_true",
        help="Download ALL apps",
    )
    parser.add_argument(
        "--build",
        "-b",
        action="store_true",
        help="Build the Magisk Module",
    )
    parser.add_argument(
        "--write-perm",
        "-wp",
        action="store_true",
        help="Write Priv-App permissions whitelist",
    )
    parser.add_argument(
        "--write-replace-list",
        "-wr",
        action="store_true",
        help="Write replace list to customize.sh",
    )
    parser.add_argument(
        "--zip",
        "-z",
        action="store_true",
        help="Zip Magisk module",
    )
    parser.add_argument(
        "--delete",
        "-D",
        action="store_true",
        help="Delete generated module folder (which contains downloaded binaries)",
    )
    parser.add_argument(
        "--push-ver",
        "-p",
        action="store_true",
        help="Push version code",
    )
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    asyncio.run(main(args))
