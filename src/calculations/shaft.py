"""轴强度计算模块

提供轴设计中的强度计算功能：
1. 截面惯性矩（极惯性矩、轴向惯性矩）
2. 抗弯截面系数
3. 抗扭截面系数
4. 临界转速计算
5. 当量直径计算（考虑键槽影响）
6. 轴径估算（按扭转强度、弯扭组合强度）
7. 标准直径系列圆整（GB/T 2822）
8. 许用扭矩/弯矩计算

核心计算公式参考机械设计手册（第六版）
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from standards.data_loader import get_standard_sizes, get_machining_allowance


@dataclass
class ShaftSection:
    """轴截面参数
    
    Attributes:
        diameter: 直径（mm）
        length: 长度（mm）
        key_slot_count: 键槽数量（0/1/2）
        key_slot_depth: 键槽深度（mm），用于当量直径计算
        material: 材料名称
    """
    diameter: float
    length: float = 0
    key_slot_count: int = 0
    key_slot_depth: float = 0
    material: str = "45"

    @property
    def radius(self) -> float:
        return self.diameter / 2.0

    @property
    def area(self) -> float:
        return math.pi * self.radius ** 2


@dataclass
class ShaftStrengthResult:
    """轴强度计算结果"""
    diameter: float
    polar_moment: float          # 极惯性矩 (mm^4)
    axial_moment_y: float        # 对Y轴惯性矩 (mm^4)
    axial_moment_z: float        # 对Z轴惯性矩 (mm^4)
    section_modulus: float       # 抗弯截面系数 (mm^3)
    torsion_modulus: float       # 抗扭截面系数 (mm^3)
    equivalent_diameter: float   # 当量直径（考虑键槽）(mm)
    critical_speed: float        # 临界转速 (rpm)
    shear_stress: float          # 剪切应力 (MPa)
    bending_stress: float        # 弯曲应力 (MPa)
    combined_stress: float       # 弯扭组合应力 (MPa)


class ShaftCalculator:
    """轴强度计算器"""

    def __init__(self, material: str = "45"):
        self.material = material
        self.material_props = self._get_material_properties(material)

    def _get_material_properties(self, material: str) -> dict:
        """获取材料属性"""
        material_data = {
            "45": {
                "yield_strength": 355,      # MPa
                "tensile_strength": 600,    # MPa
                "shear_strength": 210,      # MPa
                "elastic_modulus": 206000,  # MPa
                "poissons_ratio": 0.3,
                "density": 7850,            # kg/m^3
                "fatigue_limit": 275,       # MPa
            },
            "40Cr": {
                "yield_strength": 550,
                "tensile_strength": 980,
                "shear_strength": 330,
                "elastic_modulus": 206000,
                "poissons_ratio": 0.3,
                "density": 7850,
                "fatigue_limit": 440,
            },
            "Q235": {
                "yield_strength": 235,
                "tensile_strength": 375,
                "shear_strength": 140,
                "elastic_modulus": 206000,
                "poissons_ratio": 0.3,
                "density": 7850,
                "fatigue_limit": 170,
            },
            "20Cr": {
                "yield_strength": 540,
                "tensile_strength": 835,
                "shear_strength": 320,
                "elastic_modulus": 206000,
                "poissons_ratio": 0.3,
                "density": 7850,
                "fatigue_limit": 390,
            },
        }
        return material_data.get(material, material_data["45"])

    def polar_moment_of_inertia(self, diameter: float) -> float:
        """计算极惯性矩
        
        J_p = π * d^4 / 32
        
        Args:
            diameter: 直径（mm）
        
        Returns:
            float: 极惯性矩（mm^4）
        """
        return math.pi * diameter ** 4 / 32.0

    def axial_moment_of_inertia(self, diameter: float) -> float:
        """计算轴向惯性矩
        
        I_y = I_z = π * d^4 / 64
        
        Args:
            diameter: 直径（mm）
        
        Returns:
            float: 轴向惯性矩（mm^4）
        """
        return math.pi * diameter ** 4 / 64.0

    def section_modulus(self, diameter: float) -> float:
        """计算抗弯截面系数
        
        W = π * d^3 / 32
        
        Args:
            diameter: 直径（mm）
        
        Returns:
            float: 抗弯截面系数（mm^3）
        """
        return math.pi * diameter ** 3 / 32.0

    def torsion_modulus(self, diameter: float) -> float:
        """计算抗扭截面系数
        
        W_p = π * d^3 / 16
        
        Args:
            diameter: 直径（mm）
        
        Returns:
            float: 抗扭截面系数（mm^3）
        """
        return math.pi * diameter ** 3 / 16.0

    def equivalent_diameter(self, diameter: float, key_slot_count: int = 0, 
                           key_slot_depth: float = 0) -> float:
        """计算考虑键槽影响的当量直径
        
        单键槽：d_eq = d * (1 - 0.2 * t1 / d)
        双键槽：d_eq = d * (1 - 0.25 * t1 / d)
        
        Args:
            diameter: 实际直径（mm）
            key_slot_count: 键槽数量（0/1/2）
            key_slot_depth: 键槽深度（mm）
        
        Returns:
            float: 当量直径（mm）
        """
        if key_slot_count == 0 or key_slot_depth == 0:
            return diameter

        ratio = key_slot_depth / diameter
        if key_slot_count == 1:
            return diameter * (1 - 0.2 * ratio)
        else:
            return diameter * (1 - 0.25 * ratio)

    def estimate_diameter_by_torsion(self, torque: float, 
                                     allowable_shear_stress: float = 40) -> float:
        """按扭转强度估算轴径
        
        d ≥ (16 * T / (π * [τ]))^(1/3)
        
        Args:
            torque: 扭矩（N·mm）
            allowable_shear_stress: 许用剪切应力（MPa），默认40MPa
        
        Returns:
            float: 估算轴径（mm）
        """
        if torque <= 0:
            return 0

        diameter = (16 * torque / (math.pi * allowable_shear_stress)) ** (1/3)
        return self.round_to_standard(diameter)

    def estimate_diameter_by_bending_torsion(self, torque: float, bending_moment: float,
                                             allowable_stress: float = 60) -> float:
        """按弯扭组合强度估算轴径
        
        d ≥ (32 * sqrt(M^2 + T^2) / (π * [σ]))^(1/3)
        
        Args:
            torque: 扭矩（N·mm）
            bending_moment: 弯矩（N·mm）
            allowable_stress: 许用弯曲应力（MPa），默认60MPa
        
        Returns:
            float: 估算轴径（mm）
        """
        if torque <= 0 and bending_moment <= 0:
            return 0

        combined_moment = math.sqrt(bending_moment ** 2 + torque ** 2)
        diameter = (32 * combined_moment / (math.pi * allowable_stress)) ** (1/3)
        return self.round_to_standard(diameter)

    def calculate_allowable_torque(self, diameter: float, 
                                    allowable_shear_stress: float = None) -> float:
        """由轴径计算许用扭矩
        
        T ≤ (π * d^3 * [τ]) / 16
        
        Args:
            diameter: 轴径（mm）
            allowable_shear_stress: 许用剪切应力（MPa），默认取材料剪切强度的1/3
        
        Returns:
            float: 许用扭矩（N·mm）
        """
        if diameter <= 0:
            return 0

        if allowable_shear_stress is None:
            allowable_shear_stress = self.material_props["shear_strength"] / 3

        W_p = self.torsion_modulus(diameter)
        return W_p * allowable_shear_stress

    def calculate_allowable_bending_moment(self, diameter: float, 
                                            allowable_stress: float = None) -> float:
        """由轴径计算许用弯矩
        
        M ≤ (π * d^3 * [σ]) / 32
        
        Args:
            diameter: 轴径（mm）
            allowable_stress: 许用弯曲应力（MPa），默认取材料屈服强度的1/3
        
        Returns:
            float: 许用弯矩（N·mm）
        """
        if diameter <= 0:
            return 0

        if allowable_stress is None:
            allowable_stress = self.material_props["yield_strength"] / 3

        W = self.section_modulus(diameter)
        return W * allowable_stress

    def _get_standard_sizes(self, series: str = "first") -> list:
        """获取标准直径系列
        
        从 GB/T 2822 标准数据文件中读取标准直径系列
        
        Args:
            series: 系列类型：first（第一系列）、second（第二系列）、third（第三系列）、all（全部）
        
        Returns:
            list: 标准直径列表
        """
        return get_standard_sizes(series)

    def round_to_standard(self, diameter: float, series: str = "first", 
                          machining_allowance: float = 0) -> float:
        """将轴径圆整到标准直径系列
        
        考虑加工余量：向上圆整到最接近的标准值，减去加工余量后满足计算要求
        
        Args:
            diameter: 计算直径（mm）
            series: 系列类型：first（第一系列）、second（第二系列）、all（全部）
            machining_allowance: 加工余量（mm），默认0
        
        Returns:
            float: 标准直径（mm）
        """
        target_diameter = diameter + machining_allowance
        standard_sizes = self._get_standard_sizes(series)
        
        for size in standard_sizes:
            if size >= target_diameter:
                return size
        
        return diameter + machining_allowance

    def round_up_to_standard(self, diameter: float, series: str = "first") -> float:
        """向上圆整到标准直径系列
        
        Args:
            diameter: 计算直径（mm）
            series: 系列类型
        
        Returns:
            float: 向上圆整后的标准直径（mm）
        """
        return self.round_to_standard(diameter, series, machining_allowance=0)

    def critical_speed_simple(self, diameter: float, length: float, 
                              support_type: str = "both_ends") -> float:
        """简化临界转速计算（简支梁）
        
        n_cr = (π / 2) * sqrt(E * I / (ρ * A * L^4)) * 60
        
        Args:
            diameter: 直径（mm）
            length: 跨距（mm）
            support_type: 支撑类型：both_ends（两端简支）、cantilever（悬臂）
        
        Returns:
            float: 临界转速（rpm）
        """
        if diameter <= 0 or length <= 0:
            return 0

        E = self.material_props["elastic_modulus"] * 1000  # N/mm^2 -> N/m^2
        rho = self.material_props["density"]  # kg/m^3
        I = self.axial_moment_of_inertia(diameter) * 1e-12  # mm^4 -> m^4
        A = math.pi * (diameter / 2) ** 2 * 1e-6  # mm^2 -> m^2
        L = length * 1e-3  # mm -> m

        if support_type == "both_ends":
            factor = math.pi ** 2 / 4
        elif support_type == "cantilever":
            factor = math.pi ** 2 / 16
        else:
            factor = math.pi ** 2 / 4

        omega_cr = math.sqrt(E * I / (rho * A * L ** 4)) * math.sqrt(factor)
        n_cr = omega_cr * 60 / (2 * math.pi)

        return n_cr

    def shear_stress(self, torque: float, diameter: float) -> float:
        """计算剪切应力
        
        τ = T / W_p
        
        Args:
            torque: 扭矩（N·mm）
            diameter: 直径（mm）
        
        Returns:
            float: 剪切应力（MPa）
        """
        if diameter <= 0:
            return 0

        W_p = self.torsion_modulus(diameter)
        if W_p == 0:
            return 0

        return torque / W_p

    def bending_stress(self, bending_moment: float, diameter: float) -> float:
        """计算弯曲应力
        
        σ = M / W
        
        Args:
            bending_moment: 弯矩（N·mm）
            diameter: 直径（mm）
        
        Returns:
            float: 弯曲应力（MPa）
        """
        if diameter <= 0:
            return 0

        W = self.section_modulus(diameter)
        if W == 0:
            return 0

        return bending_moment / W

    def combined_stress(self, torque: float, bending_moment: float, 
                       diameter: float) -> float:
        """计算弯扭组合应力（第三强度理论）
        
        σ_eq = sqrt(σ^2 + 4τ^2)
        
        Args:
            torque: 扭矩（N·mm）
            bending_moment: 弯矩（N·mm）
            diameter: 直径（mm）
        
        Returns:
            float: 当量应力（MPa）
        """
        sigma = self.bending_stress(bending_moment, diameter)
        tau = self.shear_stress(torque, diameter)

        return math.sqrt(sigma ** 2 + 4 * tau ** 2)

    def calculate_all(self, diameter: float, length: float = 0, 
                     torque: float = 0, bending_moment: float = 0,
                     key_slot_count: int = 0, key_slot_depth: float = 0) -> ShaftStrengthResult:
        """计算所有强度参数
        
        Args:
            diameter: 直径（mm）
            length: 长度（mm）
            torque: 扭矩（N·mm）
            bending_moment: 弯矩（N·mm）
            key_slot_count: 键槽数量（0/1/2）
            key_slot_depth: 键槽深度（mm）
        
        Returns:
            ShaftStrengthResult: 完整计算结果
        """
        J_p = self.polar_moment_of_inertia(diameter)
        I_y = I_z = self.axial_moment_of_inertia(diameter)
        W = self.section_modulus(diameter)
        W_p = self.torsion_modulus(diameter)
        d_eq = self.equivalent_diameter(diameter, key_slot_count, key_slot_depth)
        n_cr = self.critical_speed_simple(diameter, length) if length > 0 else 0
        tau = self.shear_stress(torque, diameter)
        sigma = self.bending_stress(bending_moment, diameter)
        sigma_eq = self.combined_stress(torque, bending_moment, diameter)

        return ShaftStrengthResult(
            diameter=diameter,
            polar_moment=J_p,
            axial_moment_y=I_y,
            axial_moment_z=I_z,
            section_modulus=W,
            torsion_modulus=W_p,
            equivalent_diameter=d_eq,
            critical_speed=n_cr,
            shear_stress=tau,
            bending_stress=sigma,
            combined_stress=sigma_eq
        )

    def check_strength(self, diameter: float, torque: float, bending_moment: float,
                      key_slot_count: int = 0, key_slot_depth: float = 0) -> dict:
        """强度校核
        
        Args:
            diameter: 直径（mm）
            torque: 扭矩（N·mm）
            bending_moment: 弯矩（N·mm）
            key_slot_count: 键槽数量
            key_slot_depth: 键槽深度（mm）
        
        Returns:
            dict: 校核结果，包含各应力值及是否满足要求
        """
        d_eq = self.equivalent_diameter(diameter, key_slot_count, key_slot_depth)
        
        tau = self.shear_stress(torque, d_eq)
        sigma = self.bending_stress(bending_moment, d_eq)
        sigma_eq = self.combined_stress(torque, bending_moment, d_eq)

        tau_allow = self.material_props["shear_strength"] / 3
        sigma_allow = self.material_props["yield_strength"] / 3

        results = {
            "shear_stress": {
                "value": tau,
                "allowable": tau_allow,
                "ratio": tau / tau_allow if tau_allow > 0 else 0,
                "pass": tau <= tau_allow
            },
            "bending_stress": {
                "value": sigma,
                "allowable": sigma_allow,
                "ratio": sigma / sigma_allow if sigma_allow > 0 else 0,
                "pass": sigma <= sigma_allow
            },
            "combined_stress": {
                "value": sigma_eq,
                "allowable": sigma_allow,
                "ratio": sigma_eq / sigma_allow if sigma_allow > 0 else 0,
                "pass": sigma_eq <= sigma_allow
            },
            "equivalent_diameter": d_eq,
            "material": self.material
        }

        return results


def calculate_shaft_mass(diameter: float, length: float, density: float = 7850) -> float:
    """计算轴质量
    
    Args:
        diameter: 直径（mm）
        length: 长度（mm）
        density: 材料密度（kg/m^3），默认7850（钢材）
    
    Returns:
        float: 质量（kg）
    """
    volume = math.pi * (diameter / 2) ** 2 * length * 1e-9  # mm^3 -> m^3
    return volume * density


def calculate_torque_from_power(power: float, speed: float) -> float:
    """由功率和转速计算扭矩
    
    T = 9550 * P / n
    
    Args:
        power: 功率（kW）
        speed: 转速（rpm）
    
    Returns:
        float: 扭矩（N·m）
    """
    if speed <= 0:
        return 0
    return 9550 * power / speed