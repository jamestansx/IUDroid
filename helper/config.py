import configparser


def default_sys_path() -> dict:
    return dict(
        APP="/system/app",
        PRIVAPP="/system/priv-app",
        RESERVE="/system/reserve",
        PAPP="/system/product/app",
        PPRIVAPP="/system/product/priv-app",
        SYSEXTAPP="/system/system_ext/app",
        SYSEXTPAPP="/system/system_ext/priv-app",
    )


def read_ini(file_path: str) -> configparser.RawConfigParser:
    config = configparser.RawConfigParser(
        interpolation=configparser.ExtendedInterpolation()
    )
    config.optionxform = lambda option: option
    config.read(file_path)
    return config
