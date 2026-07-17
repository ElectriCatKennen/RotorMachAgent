import json
import os
from typing import Dict, Optional, Any


SRC_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(SRC_DIR, 'data')
STANDARDS_DIR = os.path.join(DATA_DIR, 'standards')
MATERIALS_DIR = os.path.join(DATA_DIR, 'materials')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')


_cache: Dict[str, Any] = {}


def _load_json_file(file_path: str) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _get_cached(file_name: str, dir_path: str) -> Dict[str, Any]:
    cache_key = f"{dir_path}/{file_name}"
    if cache_key not in _cache:
        file_path = os.path.join(dir_path, file_name)
        _cache[cache_key] = _load_json_file(file_path)
    return _cache[cache_key]


def load_gb_t1096() -> Dict[str, Any]:
    """加载 GB/T 1096 平键标准数据"""
    return _get_cached('GB_T1096_平键.json', STANDARDS_DIR)


def load_gb_t894() -> Dict[str, Any]:
    """加载 GB/T 894.1 弹性挡圈标准数据"""
    return _get_cached('GB_T894_1_弹性挡圈.json', STANDARDS_DIR)


def load_gb_t812() -> Dict[str, Any]:
    """加载 GB/T 812 圆螺母标准数据"""
    return _get_cached('GB_T812_圆螺母.json', STANDARDS_DIR)


def load_gb_t196() -> Dict[str, Any]:
    """加载 GB/T 196 螺纹标准数据"""
    return _get_cached('GB_T196_螺纹.json', STANDARDS_DIR)


def load_gb_t2822() -> Dict[str, Any]:
    """加载 GB/T 2822 标准尺寸系列数据"""
    return _get_cached('GB_T2822_标准尺寸.json', STANDARDS_DIR)


def get_standard_sizes(series: str = "first") -> list:
    """获取标准直径系列
    
    Args:
        series: 系列类型：first（第一系列）、second（第二系列）、third（第三系列）、all（全部）
    
    Returns:
        list: 标准直径列表
    """
    data = load_gb_t2822()
    if series == "all":
        all_sizes = []
        for s in ["first", "second", "third"]:
            all_sizes.extend(data['series'].get(s, {}).get('values', []))
        return sorted(list(set(all_sizes)))
    return data['series'].get(series, {}).get('values', [])


def get_machining_allowance(precision_level: str = "rough") -> dict:
    """获取加工余量数据
    
    Args:
        precision_level: 精度等级：rough（粗加工）、semi_finish（半精加工）、finish（精加工）、super_finish（超精加工）
    
    Returns:
        dict: 加工余量数据，包含allowance范围和surface_roughness
    """
    data = load_gb_t2822()
    return data['machining_allowance'].get(precision_level, {})


def load_materials(material_type: str = 'steel') -> Dict[str, Any]:
    """加载材料属性数据"""
    return _get_cached(f'{material_type}.json', MATERIALS_DIR)


def load_sw_templates() -> Dict[str, Any]:
    """加载 SolidWorks 模板配置"""
    return _get_cached('solidworks.json', TEMPLATES_DIR)


def load_preferred_numbers() -> Dict[str, Any]:
    """加载 GB/T 321—2005 优先数系标准数据"""
    return _get_cached('GB_T321_优先数系.json', STANDARDS_DIR)


def load_unit_conversion() -> Dict[str, Any]:
    """加载单位换算数据（GB 3100—1993）"""
    return _get_cached('GB_3100_单位换算.json', STANDARDS_DIR)


def load_mechanical_constants() -> Dict[str, Any]:
    """加载力学常数与常用公式参数"""
    return _get_cached('力学_常数.json', STANDARDS_DIR)


def get_flat_key_data(diameter: float) -> Optional[Dict[str, float]]:
    """根据轴径获取平键尺寸数据"""
    data = load_gb_t1096()
    return data['dimensions'].get(str(int(diameter)))


def get_circlip_data(diameter: float) -> Optional[Dict[str, float]]:
    """根据轴径获取弹性挡圈尺寸数据"""
    data = load_gb_t894()
    return data['dimensions'].get(str(int(diameter)))


def get_nut_data(thread_size: str) -> Optional[Dict[str, float]]:
    """根据螺纹规格获取圆螺母尺寸数据"""
    data = load_gb_t812()
    return data['dimensions'].get(thread_size)


def get_nut_groove_data(thread_size: str) -> Optional[Dict[str, float]]:
    """根据螺纹规格获取圆螺母槽尺寸数据"""
    data = load_gb_t812()
    return data['groove_dimensions'].get(thread_size)


def get_thread_data(thread_size: str) -> Optional[Dict[str, float]]:
    """根据螺纹规格获取螺纹尺寸数据"""
    data = load_gb_t196()
    return data['dimensions'].get(thread_size)


def get_key_type_data(key_type: str) -> Optional[Dict[str, Any]]:
    """获取键类型定义数据"""
    data = load_gb_t1096()
    for kt in data['key_types']:
        if kt['type'] == key_type:
            return kt
    return None


def get_length_series() -> list:
    """获取键长标准系列"""
    data = load_gb_t1096()
    return data['length_series']


def get_material_data(material_id: str) -> Optional[Dict[str, Any]]:
    """获取材料属性数据"""
    data = load_materials()
    return data['materials'].get(material_id)


def get_end_distance(diameter: float) -> Optional[Dict[str, Any]]:
    """获取键槽与轴端面的最小距离"""
    data = load_gb_t1096()
    if diameter <= 30:
        return data['end_distance'].get('≤30')
    elif diameter <= 50:
        return data['end_distance'].get('30~50')
    elif diameter <= 80:
        return data['end_distance'].get('50~80')
    else:
        return data['end_distance'].get('>80')


def clear_cache():
    """清除数据缓存"""
    _cache.clear()


def validate_data_files() -> bool:
    """验证所有数据文件是否存在"""
    required_files = [
        ('standards', 'GB_T1096_平键.json'),
        ('standards', 'GB_T894_1_弹性挡圈.json'),
        ('standards', 'GB_T812_圆螺母.json'),
        ('standards', 'GB_T196_螺纹.json'),
        ('standards', 'GB_T2822_标准尺寸.json'),
        ('standards', 'GB_T321_优先数系.json'),
        ('standards', 'GB_3100_单位换算.json'),
        ('standards', '力学_常数.json'),
        ('materials', 'steel.json'),
        ('templates', 'solidworks.json')
    ]
    
    missing = []
    for dir_name, file_name in required_files:
        file_path = os.path.join(DATA_DIR, dir_name, file_name)
        if not os.path.exists(file_path):
            missing.append(file_path)
    
    if missing:
        print(f"Missing data files: {', '.join(missing)}")
        return False
    return True