"""轴要素元类体系

轴设计的前置元类，定义构成轴的基本要素：
1. KeySlot - 键槽（平键 A/B/C 型、半圆键、楔键）
2. CirclipGroove - 弹性挡圈槽
3. Thread - 螺纹
4. ThreadRelief - 退刀槽
5. NutGroove - 圆螺母槽（含止动垫圈槽）
6. Shoulder - 轴肩
7. BearingSeat - 轴承位
8. Chamfer - 倒角
9. Radius - 圆角

每个元类都包含：
- 标准尺寸数据（从 JSON 标准表获取）
- 几何参数计算
- SW API 建模方法
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from standards.data_loader import (
    get_flat_key_data, get_circlip_data, get_nut_data,
    get_nut_groove_data, get_thread_data, get_key_type_data,
    get_length_series, get_end_distance, get_material_data
)


@dataclass
class KeySlot:
    """键槽要素

    支持 GB/T 1096 平键（A/B/C 型）、GB/T 1097 半圆键、GB/T 1563 楔键

    Attributes:
        x_center: 键槽中心 X 坐标（mm）
        length: 键槽长度（mm），必须为标准键长系列值
        diameter: 所在轴段直径（mm），用于查标准
        key_type: 键类型：flat（平键）、semi（半圆键）、wedge（楔键）
        form: 平键形式：A（圆头）、B（平头）、C（单圆头）

    Standard dimensions (auto-filled from GB tables):
        b: 键宽（mm）
        h: 键高（mm）
        t1: 轴槽深（mm）
        t2: 轮毂槽深（mm）
        arc_radius: 圆弧半径（mm），A/C型有效
        arc_radius_ratio: 圆弧半径与键宽的比值
        length_constraint: 键长约束条件
        requires_plate: 是否需要压板（C型键）
    """
    x_center: float          # 键槽中心 X 坐标（mm）
    length: float            # 键槽长度（mm）
    diameter: float          # 所在轴段直径（mm），用于查标准
    key_type: str = "flat"   # 键类型：flat（平键）、semi（半圆键）、wedge（楔键）
    form: str = "A"          # 平键形式：A（圆头）、B（平头）、C（单圆头）

    b: float = field(init=False, default=0)    # 键宽
    h: float = field(init=False, default=0)    # 键高
    t1: float = field(init=False, default=0)   # 轴槽深
    t2: float = field(init=False, default=0)   # 轮毂槽深
    arc_radius: float = field(init=False, default=0)  # 圆弧半径
    arc_radius_ratio: float = field(init=False, default=0)  # 圆弧半径比
    length_constraint: str = field(init=False, default="")  # 键长约束
    requires_plate: bool = field(init=False, default=False)  # 是否需压板

    def __post_init__(self):
        if self.key_type == "flat":
            dims = get_flat_key_data(self.diameter)
            if dims:
                self.b = dims.get("b", 0)
                self.h = dims.get("h", 0)
                self.t1 = dims.get("t1", 0)
                self.t2 = dims.get("t2", 0)
                self.arc_radius = dims.get("arc_radius", 0)

            type_data = get_key_type_data(self.form)
            if type_data:
                self.arc_radius_ratio = type_data.get("arc_radius_ratio", 0)
                self.length_constraint = type_data.get("length_constraint", "")
                self.requires_plate = type_data.get("requires_plate", False)

            if self.form == "B":
                self.arc_radius = 0
            elif self.arc_radius == 0 and self.b > 0 and self.arc_radius_ratio > 0:
                self.arc_radius = self.b * self.arc_radius_ratio

    @property
    def shaft_radius(self) -> float:
        """所在轴段半径（mm）"""
        return self.diameter / 2.0

    @property
    def x_start(self) -> float:
        """键槽起始 X 坐标（mm）"""
        if self.form == "A":
            return self.x_center - self.length / 2 + self.arc_radius
        elif self.form == "C":
            return self.x_center - self.length / 2
        else:
            return self.x_center - self.length / 2

    @property
    def x_end(self) -> float:
        """键槽结束 X 坐标（mm）"""
        if self.form == "A":
            return self.x_center + self.length / 2 - self.arc_radius
        elif self.form == "C":
            return self.x_center + self.length / 2 - self.arc_radius
        else:
            return self.x_center + self.length / 2

    @property
    def y_bottom(self) -> float:
        """键槽底部 Y 坐标（mm，距轴心）"""
        return self.shaft_radius - self.t1

    @property
    def y_top(self) -> float:
        """键槽顶部 Y 坐标（mm，距轴心）"""
        return self.shaft_radius

    @property
    def arc_center_left(self) -> Tuple[float, float]:
        """左圆弧中心坐标（mm）"""
        if self.form == "A" or self.form == "C":
            return (self.x_center - self.length / 2 + self.arc_radius,
                    self.shaft_radius - self.t1)
        return (0, 0)

    @property
    def arc_center_right(self) -> Tuple[float, float]:
        """右圆弧中心坐标（mm）"""
        if self.form == "A":
            return (self.x_center + self.length / 2 - self.arc_radius,
                    self.shaft_radius - self.t1)
        return (0, 0)

    def get_min_length(self) -> float:
        """获取键长最小值"""
        if self.form == "A":
            return 2 * self.arc_radius
        elif self.form == "C":
            return self.arc_radius
        else:
            return self.b

    def is_length_valid(self) -> bool:
        """检查键长是否符合标准系列和约束"""
        series = get_length_series()
        if self.length not in series:
            print(f'[WARN] 键长 {self.length}mm 不在标准系列中')
            return False

        if self.length < self.get_min_length():
            print(f'[WARN] 键长 {self.length}mm 小于最小允许值 {self.get_min_length()}mm')
            return False

        return True

    def is_in_standard_range(self) -> bool:
        """检查轴径是否在标准适用范围内"""
        dims = get_flat_key_data(self.diameter)
        return dims is not None

    def get_end_distance_requirement(self) -> Optional[dict]:
        """获取键槽与轴端面的距离要求"""
        return get_end_distance(self.diameter)

    def validate(self) -> bool:
        """验证键槽参数是否有效"""
        all_valid = True

        if not self.is_in_standard_range():
            print(f'[WARN] 轴径 {self.diameter}mm 不在 GB/T 1096 适用范围')
            all_valid = False

        if self.b <= 0:
            print(f'[WARN] 键槽宽度无效')
            all_valid = False

        if not self.is_length_valid():
            all_valid = False

        return all_valid


@dataclass
class CirclipGroove:
    """弹性挡圈槽要素

    支持 GB/T 894 轴用弹性挡圈槽

    Attributes:
        x_center: 槽中心 X 坐标（mm）
        diameter: 所在轴段直径（mm），用于查标准

    Standard dimensions (auto-filled from GB/T 894):
        m: 槽宽（mm），等于挡圈宽度
        n: 槽深（mm）
        d1: 槽底直径（mm）
    """
    x_center: float          # 槽中心 X 坐标（mm）
    diameter: float          # 所在轴段直径（mm），用于查标准

    m: float = field(init=False, default=0)    # 槽宽
    n: float = field(init=False, default=0)    # 槽深
    d1: float = field(init=False, default=0)   # 槽底直径

    def __post_init__(self):
        dims = get_circlip_data(self.diameter)
        if dims:
            self.m = dims.get("m", 0)
            self.n = dims.get("n", 0)
            self.d1 = dims.get("d1", 0)

    @property
    def outer_radius(self) -> float:
        """所在轴段外圆半径（mm）"""
        return self.diameter / 2.0

    @property
    def x_start(self) -> float:
        """槽起始 X 坐标（mm）"""
        return self.x_center - self.m / 2

    @property
    def x_end(self) -> float:
        """槽结束 X 坐标（mm）"""
        return self.x_center + self.m / 2

    @property
    def y_bottom(self) -> float:
        """槽底部 Y 坐标（mm，距轴心）"""
        return self.outer_radius - self.n

    @property
    def y_top(self) -> float:
        """槽顶部 Y 坐标（mm，距轴心）"""
        return self.outer_radius

    def validate(self) -> bool:
        """验证挡圈槽参数是否有效"""
        if self.m <= 0:
            print(f'[WARN] 挡圈槽宽度无效，轴径 {self.diameter}mm 无匹配标准')
            return False
        return True


@dataclass
class ThreadRelief:
    """螺纹退刀槽要素

    支持 GB/T 3 螺纹退刀槽

    Attributes:
        x_start: 退刀槽起始 X 坐标（mm）
        diameter: 螺纹公称直径（mm），用于查标准

    Standard dimensions (auto-filled from GB/T 3):
        w: 退刀槽宽度（mm）
        d3: 退刀槽底径（mm）
    """
    x_start: float           # 退刀槽起始 X 坐标（mm）
    diameter: float          # 螺纹公称直径（mm），用于查标准

    w: float = field(init=False, default=3)    # 退刀槽宽度
    d3: float = field(init=False, default=0)   # 退刀槽底径

    def __post_init__(self):
        dims = get_thread_data(f"M{int(self.diameter)}")
        if dims:
            self.w = dims.get("pitch", 1.5) * 2.0
            self.d3 = dims.get("d3", 0)

    @property
    def x_end(self) -> float:
        """退刀槽结束 X 坐标（mm）"""
        return self.x_start + self.w

    @property
    def relief_radius(self) -> float:
        """退刀槽底径半径（mm）"""
        return self.d3 / 2.0


@dataclass
class Thread:
    """螺纹要素

    支持 GB/T 196 普通螺纹

    Attributes:
        x_start: 螺纹起始 X 坐标（mm）
        length: 螺纹长度（mm）
        diameter: 螺纹公称直径（mm），用于查标准
        pitch: 螺距（mm），默认从标准表获取粗牙螺距

    Standard dimensions (auto-filled from GB/T 196):
        d1: 螺纹小径（mm）
        d2: 螺纹中径（mm）
        relief: 退刀槽要素
    """
    x_start: float           # 螺纹起始 X 坐标（mm）
    length: float            # 螺纹长度（mm）
    diameter: float          # 螺纹公称直径（mm），用于查标准
    pitch: float = 1.5       # 螺距（mm），默认粗牙

    d1: float = field(init=False, default=0)   # 小径
    d2: float = field(init=False, default=0)   # 中径
    relief: ThreadRelief = field(init=False, default=None)

    def __post_init__(self):
        dims = get_thread_data(f"M{int(self.diameter)}")
        if dims:
            self.pitch = dims.get("pitch", 1.5)
            self.d1 = dims.get("d1", 0)
            self.d2 = dims.get("d2", 0)
            self.relief = ThreadRelief(self.x_start - dims.get("pitch", 1.5) * 2.0,
                                       self.diameter)

    @property
    def x_end(self) -> float:
        """螺纹结束 X 坐标（mm）"""
        return self.x_start + self.length

    @property
    def nominal_radius(self) -> float:
        """螺纹公称半径（mm）"""
        return self.diameter / 2.0


@dataclass
class NutGroove:
    """圆螺母槽要素（含止动垫圈槽）

    支持 GB/T 812 圆螺母 + GB/T 858 止动垫圈

    Attributes:
        x_center: 槽中心 X 坐标（mm）
        diameter: 螺纹公称直径（mm），用于查标准

    Standard dimensions (auto-filled from GB/T 812):
        m: 止动垫圈槽宽（mm）
        n: 止动垫圈槽深（mm）
        D_nut: 螺母外径（mm）
        t_nut: 螺母厚度（mm）
    """
    x_center: float          # 槽中心 X 坐标（mm）
    diameter: float          # 螺纹公称直径（mm），用于查标准

    m: float = field(init=False, default=0)    # 止动垫圈槽宽
    n: float = field(init=False, default=0)    # 止动垫圈槽深
    D_nut: float = field(init=False, default=0) # 螺母外径
    t_nut: float = field(init=False, default=0) # 螺母厚度

    def __post_init__(self):
        dims = get_nut_groove_data(f"M{int(self.diameter)}")
        if dims:
            self.m = dims.get("groove_width", 0)
            self.n = dims.get("groove_depth", 0)

        nut_dims = get_nut_data(f"M{int(self.diameter)}")
        if nut_dims:
            self.D_nut = nut_dims.get("d1", 0)
            self.t_nut = nut_dims.get("m", 0)

    @property
    def shaft_radius(self) -> float:
        """螺纹段半径（mm）"""
        return self.diameter / 2.0

    @property
    def x_start(self) -> float:
        """槽起始 X 坐标（mm）"""
        return self.x_center - self.m / 2

    @property
    def x_end(self) -> float:
        """槽结束 X 坐标（mm）"""
        return self.x_center + self.m / 2

    @property
    def y_bottom(self) -> float:
        """槽底部 Y 坐标（mm，距轴心）"""
        return self.shaft_radius - self.n

    @property
    def y_top(self) -> float:
        """槽顶部 Y 坐标（mm，距轴心）"""
        return self.shaft_radius

    def validate(self) -> bool:
        """验证圆螺母槽参数是否有效"""
        if self.m <= 0:
            print(f'[WARN] 圆螺母槽宽度无效，螺纹直径 {self.diameter}mm 无匹配标准')
            return False
        return True


@dataclass
class Shoulder:
    """轴肩要素

    轴肩用于定位轴承或其他零件

    Attributes:
        x_position: 轴肩位置 X 坐标（mm）
        diameter: 轴肩直径（mm）
        length: 轴肩宽度（mm），默认 3mm
    """
    x_position: float        # 轴肩位置 X 坐标（mm）
    diameter: float          # 轴肩直径（mm）
    length: float = 3        # 轴肩宽度（mm），默认 3mm

    @property
    def radius(self) -> float:
        """轴肩半径（mm）"""
        return self.diameter / 2.0

    @property
    def x_start(self) -> float:
        """轴肩起始 X 坐标（mm）"""
        return self.x_position

    @property
    def x_end(self) -> float:
        """轴肩结束 X 坐标（mm）"""
        return self.x_position + self.length


@dataclass
class BearingSeat:
    """轴承位要素

    用于安装轴承的轴段

    Attributes:
        x_start: 轴承位起始 X 坐标（mm）
        length: 轴承位长度（mm），通常等于轴承宽度
        diameter: 轴承位直径（mm），等于轴承内径
        bearing_type: 轴承型号（如 "6207"）
    """
    x_start: float           # 轴承位起始 X 坐标（mm）
    length: float            # 轴承位长度（mm），通常等于轴承宽度
    diameter: float          # 轴承位直径（mm），等于轴承内径
    bearing_type: str = ""   # 轴承型号（如 "6207"）

    @property
    def radius(self) -> float:
        """轴承位半径（mm）"""
        return self.diameter / 2.0

    @property
    def x_end(self) -> float:
        """轴承位结束 X 坐标（mm）"""
        return self.x_start + self.length


@dataclass
class Chamfer:
    """倒角要素

    Attributes:
        x_position: 倒角位置（轴端，mm）
        size: 倒角大小（mm），默认 2×45°
        angle: 倒角角度（°），默认 45°
    """
    x_position: float        # 倒角位置（轴端，mm）
    size: float = 2          # 倒角大小（mm），默认 2×45°
    angle: float = 45        # 倒角角度（°），默认 45°


@dataclass
class Radius:
    """圆角要素

    Attributes:
        x_position: 圆角位置（轴肩过渡，mm）
        size: 圆角半径（mm），默认 2mm
    """
    x_position: float        # 圆角位置（轴肩过渡，mm）
    size: float = 2          # 圆角半径（mm），默认 2mm


@dataclass
class ShaftSegment:
    """轴段要素

    轴的基本构成单元

    Attributes:
        diameter: 轴段直径（mm）
        length: 轴段长度（mm）
        name: 功能名称
        elements: 关联要素列表
    """
    diameter: float          # 轴段直径（mm）
    length: float            # 轴段长度（mm）
    name: str = ""           # 功能名称
    elements: List[object] = field(default_factory=list)  # 关联要素

    @property
    def radius(self) -> float:
        """轴段半径（mm）"""
        return self.diameter / 2.0


def create_key_slot(x_center: float, length: float, diameter: float,
                    key_type: str = "flat", form: str = "A") -> KeySlot:
    """创建键槽要素

    Args:
        x_center: 键槽中心 X 坐标（mm）
        length: 键槽长度（mm），应为标准系列值
        diameter: 所在轴段直径（mm）
        key_type: 键类型，默认平键
        form: 平键形式，A（圆头）、B（平头）、C（单圆头）

    Returns:
        KeySlot 实例
    """
    return KeySlot(x_center, length, diameter, key_type, form)


def create_circlip_groove(x_center: float, diameter: float) -> CirclipGroove:
    """创建弹性挡圈槽要素

    Args:
        x_center: 槽中心 X 坐标（mm）
        diameter: 所在轴段直径（mm）

    Returns:
        CirclipGroove 实例
    """
    return CirclipGroove(x_center, diameter)


def create_thread(x_start: float, length: float, diameter: float,
                  pitch: float = None) -> Thread:
    """创建螺纹要素

    Args:
        x_start: 螺纹起始 X 坐标（mm）
        length: 螺纹长度（mm）
        diameter: 螺纹公称直径（mm）
        pitch: 螺距（mm），默认从标准表获取粗牙螺距

    Returns:
        Thread 实例
    """
    kwargs = {"x_start": x_start, "length": length, "diameter": diameter}
    if pitch:
        kwargs["pitch"] = pitch
    return Thread(**kwargs)


def create_nut_groove(x_center: float, diameter: float) -> NutGroove:
    """创建圆螺母槽要素

    Args:
        x_center: 槽中心 X 坐标（mm）
        diameter: 螺纹公称直径（mm）

    Returns:
        NutGroove 实例
    """
    return NutGroove(x_center, diameter)


def create_bearing_seat(x_start: float, length: float, diameter: float,
                       bearing_type: str = "") -> BearingSeat:
    """创建轴承位要素

    Args:
        x_start: 轴承位起始 X 坐标（mm）
        length: 轴承位长度（mm）
        diameter: 轴承位直径（mm）
        bearing_type: 轴承型号（可选）

    Returns:
        BearingSeat 实例
    """
    return BearingSeat(x_start, length, diameter, bearing_type)