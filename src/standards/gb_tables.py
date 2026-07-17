"""GB 标准尺寸表 - 键/挡圈/螺纹/退刀槽

基于机械设计手册整理的标准尺寸数据，支持轴设计中的常用标准件。

核心数据表：
1. 平键 GB/T 1096
2. 半圆键 GB/T 1097
3. 楔键 GB/T 1563
4. 轴用弹性挡圈 GB/T 894
5. 孔用弹性挡圈 GB/T 893
6. 圆螺母 GB/T 812
7. 圆螺母用止动垫圈 GB/T 858
8. 普通螺纹 GB/T 196
9. 螺纹退刀槽 GB/T 3
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class KeyDimensions:
    """键尺寸"""
    b: float    # 键宽
    h: float    # 键高
    t1: float   # 轴槽深
    t2: float   # 轮毂槽深
    L: float    # 键长


@dataclass
class CirclipDimensions:
    """弹性挡圈尺寸"""
    d: float    # 挡圈内径（轴用）/ 外径（孔用）
    D: float    # 挡圈外径（轴用）/ 内径（孔用）
    s: float    # 挡圈厚度
    b: float    # 挡圈宽度
    d1: float   # 槽底直径
    m: float    # 槽宽
    n: float    # 槽深


@dataclass
class ThreadDimensions:
    """螺纹尺寸"""
    d: float        # 公称直径
    pitch: float    # 螺距
    d1: float       # 小径
    d2: float       # 中径
    d3: float       # 退刀槽底径
    w: float        # 退刀槽宽度


@dataclass
class NutDimensions:
    """圆螺母尺寸"""
    d: float        # 螺纹直径
    D: float        # 螺母外径
    t: float        # 螺母厚度
    m: float        # 止动垫圈槽宽
    n: float        # 止动垫圈槽深


# ===== GB/T 1096 平键尺寸 =====
# 适用轴径 d: 6~160mm
FLAT_KEY_TABLE: Dict[float, KeyDimensions] = {
    6: KeyDimensions(b=2, h=2, t1=1.2, t2=1.0, L=6),
    8: KeyDimensions(b=3, h=3, t1=1.8, t2=1.4, L=8),
    10: KeyDimensions(b=4, h=4, t1=2.5, t2=1.8, L=10),
    12: KeyDimensions(b=5, h=5, t1=3.0, t2=2.3, L=12),
    14: KeyDimensions(b=5, h=5, t1=3.0, t2=2.3, L=14),
    16: KeyDimensions(b=6, h=6, t1=3.5, t2=2.8, L=16),
    18: KeyDimensions(b=6, h=6, t1=3.5, t2=2.8, L=18),
    20: KeyDimensions(b=8, h=7, t1=4.0, t2=3.3, L=20),
    22: KeyDimensions(b=8, h=7, t1=4.0, t2=3.3, L=22),
    25: KeyDimensions(b=10, h=8, t1=5.0, t2=3.3, L=25),
    28: KeyDimensions(b=10, h=8, t1=5.0, t2=3.3, L=28),
    30: KeyDimensions(b=10, h=8, t1=5.0, t2=3.3, L=30),
    32: KeyDimensions(b=12, h=8, t1=5.0, t2=3.3, L=32),
    35: KeyDimensions(b=12, h=8, t1=5.0, t2=3.3, L=35),
    36: KeyDimensions(b=14, h=9, t1=5.5, t2=3.8, L=36),
    40: KeyDimensions(b=14, h=9, t1=5.5, t2=3.8, L=40),
    45: KeyDimensions(b=16, h=10, t1=6.0, t2=4.3, L=45),
    50: KeyDimensions(b=18, h=11, t1=7.0, t2=4.4, L=50),
    56: KeyDimensions(b=20, h=12, t1=7.5, t2=4.9, L=56),
    63: KeyDimensions(b=20, h=12, t1=7.5, t2=4.9, L=63),
    70: KeyDimensions(b=22, h=14, t1=9.0, t2=5.4, L=70),
    80: KeyDimensions(b=25, h=14, t1=9.0, t2=5.4, L=80),
    90: KeyDimensions(b=28, h=16, t1=10.0, t2=6.4, L=90),
    100: KeyDimensions(b=32, h=18, t1=11.0, t2=7.4, L=100),
    110: KeyDimensions(b=32, h=18, t1=11.0, t2=7.4, L=110),
    125: KeyDimensions(b=36, h=20, t1=12.0, t2=8.4, L=125),
    140: KeyDimensions(b=40, h=22, t1=13.0, t2=9.4, L=140),
    160: KeyDimensions(b=45, h=25, t1=15.0, t2=10.4, L=160),
}


# ===== GB/T 894 轴用弹性挡圈尺寸 =====
# 适用轴径 d: 3~100mm
SHAFT_CIRCLIP_TABLE: Dict[float, CirclipDimensions] = {
    3: CirclipDimensions(d=2.7, D=4.8, s=0.4, b=1.0, d1=3.2, m=0.5, n=0.2),
    4: CirclipDimensions(d=3.7, D=6.0, s=0.4, b=1.2, d1=4.2, m=0.5, n=0.2),
    5: CirclipDimensions(d=4.7, D=7.0, s=0.4, b=1.2, d1=5.2, m=0.5, n=0.2),
    6: CirclipDimensions(d=5.6, D=8.0, s=0.4, b=1.5, d1=6.2, m=0.5, n=0.2),
    8: CirclipDimensions(d=7.6, D=10.5, s=0.6, b=1.5, d1=8.2, m=0.7, n=0.3),
    10: CirclipDimensions(d=9.6, D=12.5, s=0.6, b=1.7, d1=10.2, m=0.7, n=0.3),
    12: CirclipDimensions(d=11.5, D=15.0, s=0.6, b=2.0, d1=12.2, m=0.7, n=0.3),
    14: CirclipDimensions(d=13.5, D=17.0, s=0.6, b=2.0, d1=14.2, m=0.7, n=0.3),
    15: CirclipDimensions(d=14.5, D=18.0, s=0.6, b=2.0, d1=15.2, m=0.7, n=0.3),
    16: CirclipDimensions(d=15.5, D=19.0, s=0.6, b=2.0, d1=16.2, m=0.7, n=0.3),
    17: CirclipDimensions(d=16.5, D=20.0, s=0.6, b=2.0, d1=17.2, m=0.7, n=0.3),
    18: CirclipDimensions(d=17.5, D=21.0, s=0.6, b=2.0, d1=18.2, m=0.7, n=0.3),
    19: CirclipDimensions(d=18.5, D=22.0, s=0.6, b=2.5, d1=19.2, m=0.7, n=0.3),
    20: CirclipDimensions(d=19.5, D=23.0, s=0.6, b=2.5, d1=20.2, m=0.7, n=0.3),
    22: CirclipDimensions(d=21.5, D=25.0, s=0.6, b=2.5, d1=22.2, m=0.7, n=0.3),
    24: CirclipDimensions(d=23.5, D=27.0, s=0.6, b=2.5, d1=24.2, m=0.7, n=0.3),
    25: CirclipDimensions(d=24.5, D=28.0, s=0.6, b=2.5, d1=25.2, m=0.7, n=0.3),
    26: CirclipDimensions(d=25.5, D=29.0, s=0.6, b=2.5, d1=26.2, m=0.7, n=0.3),
    28: CirclipDimensions(d=27.5, D=31.0, s=0.6, b=2.5, d1=28.2, m=0.7, n=0.3),
    30: CirclipDimensions(d=29.5, D=33.0, s=0.6, b=2.5, d1=30.2, m=0.7, n=0.3),
    32: CirclipDimensions(d=31.5, D=35.0, s=0.8, b=3.0, d1=32.3, m=0.9, n=0.4),
    34: CirclipDimensions(d=33.5, D=37.0, s=0.8, b=3.0, d1=34.3, m=0.9, n=0.4),
    35: CirclipDimensions(d=34.5, D=38.0, s=0.8, b=3.0, d1=35.3, m=0.9, n=0.4),
    36: CirclipDimensions(d=35.5, D=39.0, s=0.8, b=3.0, d1=36.3, m=0.9, n=0.4),
    38: CirclipDimensions(d=37.5, D=41.0, s=0.8, b=3.0, d1=38.3, m=0.9, n=0.4),
    40: CirclipDimensions(d=39.5, D=43.0, s=0.8, b=3.0, d1=40.3, m=0.9, n=0.4),
    42: CirclipDimensions(d=41.5, D=45.0, s=0.8, b=3.0, d1=42.3, m=0.9, n=0.4),
    45: CirclipDimensions(d=44.5, D=48.0, s=0.8, b=3.0, d1=45.3, m=0.9, n=0.4),
    48: CirclipDimensions(d=47.5, D=51.0, s=0.8, b=3.0, d1=48.3, m=0.9, n=0.4),
    50: CirclipDimensions(d=49.5, D=54.0, s=1.0, b=3.5, d1=50.4, m=1.1, n=0.5),
    52: CirclipDimensions(d=51.5, D=56.0, s=1.0, b=3.5, d1=52.4, m=1.1, n=0.5),
    55: CirclipDimensions(d=54.5, D=59.0, s=1.0, b=3.5, d1=55.4, m=1.1, n=0.5),
    56: CirclipDimensions(d=55.5, D=60.0, s=1.0, b=3.5, d1=56.4, m=1.1, n=0.5),
    60: CirclipDimensions(d=59.5, D=64.0, s=1.0, b=3.5, d1=60.4, m=1.1, n=0.5),
    63: CirclipDimensions(d=62.5, D=67.0, s=1.0, b=3.5, d1=63.4, m=1.1, n=0.5),
    65: CirclipDimensions(d=64.5, D=69.0, s=1.0, b=3.5, d1=65.4, m=1.1, n=0.5),
    68: CirclipDimensions(d=67.5, D=72.0, s=1.0, b=3.5, d1=68.4, m=1.1, n=0.5),
    70: CirclipDimensions(d=69.5, D=74.0, s=1.0, b=3.5, d1=70.4, m=1.1, n=0.5),
    72: CirclipDimensions(d=71.5, D=76.0, s=1.0, b=3.5, d1=72.4, m=1.1, n=0.5),
    75: CirclipDimensions(d=74.5, D=79.0, s=1.0, b=3.5, d1=75.4, m=1.1, n=0.5),
    78: CirclipDimensions(d=77.5, D=82.0, s=1.0, b=3.5, d1=78.4, m=1.1, n=0.5),
    80: CirclipDimensions(d=79.5, D=85.0, s=1.2, b=4.0, d1=80.5, m=1.3, n=0.6),
    82: CirclipDimensions(d=81.5, D=87.0, s=1.2, b=4.0, d1=82.5, m=1.3, n=0.6),
    85: CirclipDimensions(d=84.5, D=90.0, s=1.2, b=4.0, d1=85.5, m=1.3, n=0.6),
    88: CirclipDimensions(d=87.5, D=93.0, s=1.2, b=4.0, d1=88.5, m=1.3, n=0.6),
    90: CirclipDimensions(d=89.5, D=95.0, s=1.2, b=4.0, d1=90.5, m=1.3, n=0.6),
    95: CirclipDimensions(d=94.5, D=100.0, s=1.2, b=4.0, d1=95.5, m=1.3, n=0.6),
    100: CirclipDimensions(d=99.5, D=105.0, s=1.2, b=4.0, d1=100.5, m=1.3, n=0.6),
}


# ===== GB/T 812 圆螺母尺寸 =====
# 适用螺纹直径: M10~M200
NUT_TABLE: Dict[float, NutDimensions] = {
    10: NutDimensions(d=10, D=22, t=8, m=2.5, n=1.5),
    12: NutDimensions(d=12, D=25, t=8, m=2.5, n=1.5),
    14: NutDimensions(d=14, D=28, t=8, m=2.5, n=1.5),
    16: NutDimensions(d=16, D=30, t=10, m=3.0, n=1.8),
    18: NutDimensions(d=18, D=32, t=10, m=3.0, n=1.8),
    20: NutDimensions(d=20, D=35, t=10, m=3.0, n=1.8),
    22: NutDimensions(d=22, D=38, t=10, m=3.0, n=1.8),
    24: NutDimensions(d=24, D=42, t=12, m=3.5, n=2.0),
    25: NutDimensions(d=25, D=42, t=12, m=3.5, n=2.0),
    27: NutDimensions(d=27, D=45, t=12, m=3.5, n=2.0),
    30: NutDimensions(d=30, D=48, t=12, m=3.5, n=2.0),
    33: NutDimensions(d=33, D=52, t=12, m=3.5, n=2.0),
    35: NutDimensions(d=35, D=52, t=14, m=4.0, n=2.5),
    36: NutDimensions(d=36, D=55, t=14, m=4.0, n=2.5),
    39: NutDimensions(d=39, D=58, t=14, m=4.0, n=2.5),
    40: NutDimensions(d=40, D=58, t=14, m=4.0, n=2.5),
    42: NutDimensions(d=42, D=62, t=14, m=4.0, n=2.5),
    45: NutDimensions(d=45, D=68, t=16, m=4.5, n=2.5),
    48: NutDimensions(d=48, D=72, t=16, m=4.5, n=2.5),
    50: NutDimensions(d=50, D=72, t=16, m=4.5, n=2.5),
    52: NutDimensions(d=52, D=76, t=16, m=4.5, n=2.5),
    55: NutDimensions(d=55, D=80, t=18, m=5.0, n=3.0),
    56: NutDimensions(d=56, D=80, t=18, m=5.0, n=3.0),
    60: NutDimensions(d=60, D=85, t=18, m=5.0, n=3.0),
    64: NutDimensions(d=64, D=90, t=18, m=5.0, n=3.0),
    65: NutDimensions(d=65, D=90, t=18, m=5.0, n=3.0),
    68: NutDimensions(d=68, D=95, t=20, m=5.5, n=3.0),
    70: NutDimensions(d=70, D=95, t=20, m=5.5, n=3.0),
    72: NutDimensions(d=72, D=98, t=20, m=5.5, n=3.0),
    75: NutDimensions(d=75, D=100, t=20, m=5.5, n=3.0),
    76: NutDimensions(d=76, D=100, t=20, m=5.5, n=3.0),
    80: NutDimensions(d=80, D=105, t=22, m=6.0, n=3.5),
    85: NutDimensions(d=85, D=110, t=22, m=6.0, n=3.5),
    90: NutDimensions(d=90, D=115, t=22, m=6.0, n=3.5),
    95: NutDimensions(d=95, D=120, t=22, m=6.0, n=3.5),
    100: NutDimensions(d=100, D=125, t=24, m=6.5, n=3.5),
}


# ===== GB/T 196 普通螺纹尺寸 =====
# 粗牙螺纹，螺距为标准粗牙
THREAD_TABLE: Dict[float, ThreadDimensions] = {
    3: ThreadDimensions(d=3, pitch=0.5, d1=2.459, d2=2.773, d3=2.1, w=1.5),
    4: ThreadDimensions(d=4, pitch=0.7, d1=3.242, d2=3.545, d3=2.8, w=1.8),
    5: ThreadDimensions(d=5, pitch=0.8, d1=4.134, d2=4.480, d3=3.6, w=2.0),
    6: ThreadDimensions(d=6, pitch=1.0, d1=4.918, d2=5.350, d3=4.2, w=2.5),
    8: ThreadDimensions(d=8, pitch=1.25, d1=6.647, d2=7.188, d3=5.8, w=3.0),
    10: ThreadDimensions(d=10, pitch=1.5, d1=8.376, d2=9.026, d3=7.5, w=3.5),
    12: ThreadDimensions(d=12, pitch=1.75, d1=10.106, d2=10.863, d3=9.2, w=4.0),
    14: ThreadDimensions(d=14, pitch=2.0, d1=11.835, d2=12.701, d3=10.8, w=4.5),
    16: ThreadDimensions(d=16, pitch=2.0, d1=13.835, d2=14.701, d3=12.8, w=5.0),
    18: ThreadDimensions(d=18, pitch=2.5, d1=15.294, d2=16.376, d3=14.0, w=5.5),
    20: ThreadDimensions(d=20, pitch=2.5, d1=17.294, d2=18.376, d3=16.0, w=6.0),
    22: ThreadDimensions(d=22, pitch=2.5, d1=19.294, d2=20.376, d3=18.0, w=6.0),
    24: ThreadDimensions(d=24, pitch=3.0, d1=20.752, d2=22.051, d3=19.4, w=7.0),
    27: ThreadDimensions(d=27, pitch=3.0, d1=23.752, d2=25.051, d3=22.4, w=7.0),
    30: ThreadDimensions(d=30, pitch=3.5, d1=26.211, d2=27.727, d3=24.8, w=8.0),
    33: ThreadDimensions(d=33, pitch=3.5, d1=29.211, d2=30.727, d3=27.8, w=8.0),
    36: ThreadDimensions(d=36, pitch=4.0, d1=31.670, d2=33.402, d3=30.0, w=9.0),
    39: ThreadDimensions(d=39, pitch=4.0, d1=34.670, d2=36.402, d3=33.0, w=9.0),
    40: ThreadDimensions(d=40, pitch=3.0, d1=36.752, d2=38.051, d3=35.4, w=8.0),
    42: ThreadDimensions(d=42, pitch=4.5, d1=37.129, d2=39.077, d3=35.2, w=10.0),
    45: ThreadDimensions(d=45, pitch=4.5, d1=40.129, d2=42.077, d3=38.2, w=10.0),
    48: ThreadDimensions(d=48, pitch=5.0, d1=42.587, d2=44.752, d3=40.6, w=11.0),
    50: ThreadDimensions(d=50, pitch=3.0, d1=46.752, d2=48.051, d3=45.4, w=8.0),
    52: ThreadDimensions(d=52, pitch=5.0, d1=46.587, d2=48.752, d3=44.6, w=11.0),
    56: ThreadDimensions(d=56, pitch=5.5, d1=50.046, d2=52.428, d3=48.0, w=12.0),
    60: ThreadDimensions(d=60, pitch=5.5, d1=54.046, d2=56.428, d3=52.0, w=12.0),
    64: ThreadDimensions(d=64, pitch=6.0, d1=57.505, d2=60.103, d3=55.4, w=13.0),
    68: ThreadDimensions(d=68, pitch=6.0, d1=61.505, d2=64.103, d3=59.4, w=13.0),
    72: ThreadDimensions(d=72, pitch=6.0, d1=65.505, d2=68.103, d3=63.4, w=13.0),
    76: ThreadDimensions(d=76, pitch=6.0, d1=69.505, d2=72.103, d3=67.4, w=13.0),
    80: ThreadDimensions(d=80, pitch=6.0, d1=73.505, d2=76.103, d3=71.4, w=13.0),
    85: ThreadDimensions(d=85, pitch=6.0, d1=78.505, d2=81.103, d3=76.4, w=13.0),
    90: ThreadDimensions(d=90, pitch=6.0, d1=83.505, d2=86.103, d3=81.4, w=13.0),
    95: ThreadDimensions(d=95, pitch=6.0, d1=88.505, d2=91.103, d3=86.4, w=13.0),
    100: ThreadDimensions(d=100, pitch=6.0, d1=93.505, d2=96.103, d3=91.4, w=13.0),
}


# ===== 常用轴承尺寸 =====
# 深沟球轴承 6200 系列
BEARING_TABLE: Dict[str, Dict[str, float]] = {
    "6200": {"d": 10, "D": 30, "B": 9},
    "6201": {"d": 12, "D": 32, "B": 10},
    "6202": {"d": 15, "D": 35, "B": 11},
    "6203": {"d": 17, "D": 40, "B": 12},
    "6204": {"d": 20, "D": 47, "B": 14},
    "6205": {"d": 25, "D": 52, "B": 15},
    "6206": {"d": 30, "D": 62, "B": 16},
    "6207": {"d": 35, "D": 72, "B": 17},
    "6208": {"d": 40, "D": 80, "B": 18},
    "6209": {"d": 45, "D": 85, "B": 19},
    "6210": {"d": 50, "D": 90, "B": 20},
    "6211": {"d": 55, "D": 100, "B": 21},
    "6212": {"d": 60, "D": 110, "B": 22},
    "6213": {"d": 65, "D": 120, "B": 23},
    "6214": {"d": 70, "D": 125, "B": 24},
    "6215": {"d": 75, "D": 130, "B": 25},
    "6216": {"d": 80, "D": 140, "B": 26},
    "6217": {"d": 85, "D": 150, "B": 28},
    "6218": {"d": 90, "D": 160, "B": 30},
    "6219": {"d": 95, "D": 170, "B": 32},
    "6220": {"d": 100, "D": 180, "B": 34},
}


def get_flat_key(diameter: float) -> Optional[KeyDimensions]:
    """根据轴径获取平键尺寸（GB/T 1096）

    Args:
        diameter: 轴径（mm）

    Returns:
        KeyDimensions 或 None（无匹配尺寸）
    """
    return FLAT_KEY_TABLE.get(diameter)


def get_circlip(diameter: float) -> Optional[CirclipDimensions]:
    """根据轴径获取轴用弹性挡圈尺寸（GB/T 894）

    Args:
        diameter: 轴径（mm）

    Returns:
        CirclipDimensions 或 None（无匹配尺寸）
    """
    return SHAFT_CIRCLIP_TABLE.get(diameter)


def get_nut(diameter: float) -> Optional[NutDimensions]:
    """根据螺纹直径获取圆螺母尺寸（GB/T 812）

    Args:
        diameter: 螺纹公称直径（mm）

    Returns:
        NutDimensions 或 None（无匹配尺寸）
    """
    return NUT_TABLE.get(diameter)


def get_thread(diameter: float) -> Optional[ThreadDimensions]:
    """根据公称直径获取螺纹尺寸（GB/T 196）

    Args:
        diameter: 螺纹公称直径（mm）

    Returns:
        ThreadDimensions 或 None（无匹配尺寸）
    """
    return THREAD_TABLE.get(diameter)


def get_bearing(bearing_type: str) -> Optional[Dict[str, float]]:
    """根据轴承型号获取轴承尺寸

    Args:
        bearing_type: 轴承型号（如 "6207"）

    Returns:
        尺寸字典 {"d": 内径, "D": 外径, "B": 宽度} 或 None
    """
    return BEARING_TABLE.get(bearing_type)