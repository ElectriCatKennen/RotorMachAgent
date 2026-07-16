"""SW 版本检测 - 运行时检测 SolidWorks 版本

支持通过注册表、安装目录、COM 对象三种方式检测 SW 版本。
"""

import winreg
import glob
import subprocess
import re


def detect_sw_version() -> str:
    """检测 SOLIDWORKS 版本

    按优先级尝试三种方法：
    1. COM 对象（已运行时）
    2. 注册表
    3. 安装目录

    Returns:
        版本号字符串，如 "2023"、"2024"，失败返回空字符串
    """
    version = _detect_via_com()
    if version:
        return version

    version = _detect_via_registry()
    if version:
        return version

    version = _detect_via_install_dir()
    if version:
        return version

    return ""


def _detect_via_com() -> str:
    """通过 COM 对象检测版本（SW 已运行时）"""
    try:
        import win32com.client
        sw_app = win32com.client.GetActiveObject('SldWorks.Application')
        rev = sw_app.RevisionNumber
        return _revision_to_version(rev)
    except Exception:
        return ""


def _detect_via_registry() -> str:
    """通过注册表检测版本"""
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\SolidWorks\Installed Products"
        ) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        value, _ = winreg.QueryValueEx(subkey, "Version")
                        return str(value)
                except OSError:
                    break
                i += 1
    except Exception:
        pass

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\SolidWorks\Installed Products"
        ) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        value, _ = winreg.QueryValueEx(subkey, "Version")
                        return str(value)
                except OSError:
                    break
                i += 1
    except Exception:
        pass

    return ""


def _detect_via_install_dir() -> str:
    """通过安装目录检测版本"""
    patterns = [
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS *",
        r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS *"
    ]

    for pattern in patterns:
        dirs = glob.glob(pattern)
        if dirs:
            for d in dirs:
                match = re.search(r'SOLIDWORKS (\d{4})', d)
                if match:
                    return match.group(1)
    return ""


def _revision_to_version(revision: str) -> str:
    """将 RevisionNumber 转换为版本号

    SW 版本对应关系：
    - 2023: Revision 31.x.x
    - 2024: Revision 32.x.x
    - 2025: Revision 33.x.x

    Args:
        revision: SW.RevisionNumber 返回值，如 "31.5.0"

    Returns:
        版本号字符串，如 "2023"
    """
    try:
        major = int(revision.split('.')[0])
        version = 1992 + major
        return str(version)
    except Exception:
        return ""


def get_sw_install_path(version: str = "") -> str:
    """获取 SOLIDWORKS 安装路径

    Args:
        version: 指定版本号，为空时自动检测

    Returns:
        安装路径字符串，失败返回空字符串
    """
    if not version:
        version = detect_sw_version()
        if not version:
            return ""

    paths = [
        rf"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS {version}",
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"
    ]

    for path in paths:
        if glob.glob(path):
            return path
    return ""


def get_sw_tlb_path(version: str = "") -> str:
    """获取 SOLIDWORKS 类型库路径

    Args:
        version: 指定版本号，为空时自动检测

    Returns:
        sldworks.tlb 路径字符串，失败返回空字符串
    """
    install_path = get_sw_install_path(version)
    if install_path:
        tlb_path = f"{install_path}\\sldworks.tlb"
        if glob.glob(tlb_path):
            return tlb_path
    return ""


def is_sw_running() -> bool:
    """检测 SOLIDWORKS 是否正在运行"""
    result = subprocess.run(
        ['tasklist', '/FI', 'IMAGENAME eq sldworks.exe'],
        capture_output=True, text=True
    )
    return 'sldworks.exe' in result.stdout