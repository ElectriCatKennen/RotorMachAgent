"""轴要素配合约束系统

提供轴设计中的约束检查功能：
1. 距离约束：键槽与轴端面、要素之间的最小距离
2. 壁厚约束：钻孔后的剩余壁厚检查
3. 干涉检测：要素之间的几何干涉检测

核心约束规则：
- A型键槽距轴端面最小距离（GB/T 1096）
- C型键槽距轴端面最小距离（GB/T 1096）
- 钻孔后剩余壁厚要求
- 要素重叠检测
- 退刀槽与相邻要素的距离要求
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import math


@dataclass
class ConstraintViolation:
    """约束违反记录"""
    type: str               # 约束类型
    element1: str           # 要素1名称
    element2: str           # 要素2名称（可选）
    min_distance: float     # 最小允许距离（mm）
    actual_distance: float  # 实际距离（mm）
    severity: str           # 严重程度: warning | error
    message: str            # 详细描述


@dataclass
class DrillHole:
    """钻孔要素
    
    Attributes:
        x_center: 孔中心 X 坐标（mm）
        y_center: 孔中心 Y 坐标（mm），距轴心
        diameter: 孔径（mm）
        depth: 孔深（mm）
        name: 孔名称
    """
    x_center: float
    y_center: float
    diameter: float
    depth: float = 10
    name: str = "drill_hole"

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


class ConstraintChecker:
    """约束检查器
    
    提供轴设计中各种约束的检查功能
    """

    def __init__(self):
        self.violations: List[ConstraintViolation] = []

    def clear(self):
        """清除所有约束违反记录"""
        self.violations.clear()

    def check_key_end_distance(self, key_slot, shaft_length: float, 
                               shaft_start_x: float = 0) -> bool:
        """检查键槽与轴端面的距离是否满足要求
        
        Args:
            key_slot: 键槽要素
            shaft_length: 轴总长（mm）
            shaft_start_x: 轴起始 X 坐标（mm）
        
        Returns:
            bool: 是否满足约束
        """
        end_dist = key_slot.get_end_distance_requirement()
        if not end_dist:
            return True

        min_dist = end_dist['min']
        shaft_end_x = shaft_start_x + shaft_length

        if key_slot.form == 'A':
            dist_to_start = key_slot.x_start - shaft_start_x
            dist_to_end = shaft_end_x - key_slot.x_end

            violations = []
            if dist_to_start < min_dist:
                violations.append((dist_to_start, "轴左端面"))
            if dist_to_end < min_dist:
                violations.append((dist_to_end, "轴右端面"))

            for dist, face_name in violations:
                self.violations.append(ConstraintViolation(
                    type="key_end_distance",
                    element1=f"A型键槽(L={key_slot.length})",
                    element2=face_name,
                    min_distance=min_dist,
                    actual_distance=dist,
                    severity="warning",
                    message=f"A型键槽距{face_name}距离{dist:.1f}mm < 最小{min_dist}mm"
                ))

            return len(violations) == 0

        elif key_slot.form == 'C':
            dist_to_near_end = min(
                key_slot.x_start - shaft_start_x,
                shaft_end_x - key_slot.x_start
            )
            if dist_to_near_end < min_dist:
                self.violations.append(ConstraintViolation(
                    type="key_end_distance",
                    element1=f"C型键槽(L={key_slot.length})",
                    element2="轴端面",
                    min_distance=min_dist,
                    actual_distance=dist_to_near_end,
                    severity="warning",
                    message=f"C型键槽距轴端面距离{dist_to_near_end:.1f}mm < 最小{min_dist}mm"
                ))
                return False

        return True

    def check_drill_wall_thickness(self, hole: DrillHole, shaft_radius: float) -> bool:
        """检查钻孔后的剩余壁厚
        
        剩余壁厚 = 轴半径 - 孔中心到轴心距离 - 孔径/2
        
        硬约束：剩余壁厚 ≥ 3mm（最极限情况）
        建议约束：剩余壁厚 ≥ max(3mm, 轴半径×15%)
        
        Args:
            hole: 钻孔要素
            shaft_radius: 轴段半径（mm）
        
        Returns:
            bool: 是否满足约束
        """
        remaining_wall = shaft_radius - hole.y_center - hole.radius

        min_wall_hard = 3.0
        min_wall_ratio = 0.15
        min_wall_recommend = max(min_wall_hard, shaft_radius * min_wall_ratio)

        if remaining_wall < min_wall_hard:
            self.violations.append(ConstraintViolation(
                type="drill_wall_thickness",
                element1=f"钻孔({hole.diameter}mm)",
                element2=f"轴段(R={shaft_radius}mm)",
                min_distance=min_wall_hard,
                actual_distance=remaining_wall,
                severity="error",
                message=f"钻孔后剩余壁厚{remaining_wall:.2f}mm < 最小3mm，有钻破壁风险"
            ))
            return False

        elif remaining_wall < min_wall_recommend:
            self.violations.append(ConstraintViolation(
                type="drill_wall_thickness",
                element1=f"钻孔({hole.diameter}mm)",
                element2=f"轴段(R={shaft_radius}mm)",
                min_distance=min_wall_recommend,
                actual_distance=remaining_wall,
                severity="warning",
                message=f"钻孔后剩余壁厚{remaining_wall:.2f}mm接近最小允许值，建议增加轴径或减小孔径"
            ))

        return True

    def check_element_overlap(self, element1, element2, tolerance: float = 0.1) -> bool:
        """检查两个要素是否重叠
        
        Args:
            element1: 要素1（需有x_start, x_end属性）
            element2: 要素2（需有x_start, x_end属性）
            tolerance: 容差（mm）
        
        Returns:
            bool: 是否存在重叠
        """
        if not hasattr(element1, 'x_start') or not hasattr(element1, 'x_end'):
            return True
        if not hasattr(element2, 'x_start') or not hasattr(element2, 'x_end'):
            return True

        e1_start, e1_end = element1.x_start, element1.x_end
        e2_start, e2_end = element2.x_start, element2.x_end

        overlap_start = max(e1_start, e2_start)
        overlap_end = min(e1_end, e2_end)

        overlap_length = overlap_end - overlap_start

        if overlap_length > tolerance:
            self.violations.append(ConstraintViolation(
                type="element_overlap",
                element1=type(element1).__name__,
                element2=type(element2).__name__,
                min_distance=tolerance,
                actual_distance=-overlap_length,
                severity="error",
                message=f"要素重叠：{type(element1).__name__}与{type(element2).__name__}重叠长度{overlap_length:.2f}mm"
            ))
            return False

        return True

    def check_elements_proximity(self, element1, element2, min_distance: float) -> bool:
        """检查两个要素之间的距离是否满足最小距离要求
        
        Args:
            element1: 要素1（需有x_start, x_end属性）
            element2: 要素2（需有x_start, x_end属性）
            min_distance: 最小允许距离（mm）
        
        Returns:
            bool: 是否满足约束
        """
        if not hasattr(element1, 'x_start') or not hasattr(element1, 'x_end'):
            return True
        if not hasattr(element2, 'x_start') or not hasattr(element2, 'x_end'):
            return True

        e1_start, e1_end = element1.x_start, element1.x_end
        e2_start, e2_end = element2.x_start, element2.x_end

        if e1_end < e2_start:
            gap = e2_start - e1_end
        elif e2_end < e1_start:
            gap = e1_start - e2_end
        else:
            gap = 0

        if gap < min_distance:
            self.violations.append(ConstraintViolation(
                type="element_proximity",
                element1=type(element1).__name__,
                element2=type(element2).__name__,
                min_distance=min_distance,
                actual_distance=gap,
                severity="warning",
                message=f"要素间距不足：{type(element1).__name__}与{type(element2).__name__}距离{gap:.2f}mm < 最小{min_distance}mm"
            ))
            return False

        return True

    def check_thread_relief_clearance(self, thread, other_element) -> bool:
        """检查退刀槽与相邻要素的距离
        
        Args:
            thread: 螺纹要素
            other_element: 相邻要素
        
        Returns:
            bool: 是否满足约束
        """
        if not thread.relief:
            return True

        relief_start = thread.relief.x_start
        relief_end = thread.relief.x_end

        if hasattr(other_element, 'x_start') and hasattr(other_element, 'x_end'):
            elem_start, elem_end = other_element.x_start, other_element.x_end

            gap_to_relief = min(abs(elem_end - relief_start), abs(elem_start - relief_end))

            min_clearance = 1.0

            if gap_to_relief < min_clearance:
                self.violations.append(ConstraintViolation(
                    type="thread_relief_clearance",
                    element1="退刀槽",
                    element2=type(other_element).__name__,
                    min_distance=min_clearance,
                    actual_distance=gap_to_relief,
                    severity="warning",
                    message=f"退刀槽与{type(other_element).__name__}距离{gap_to_relief:.2f}mm < 最小{min_clearance}mm"
                ))
                return False

        return True

    def check_circlip_groove_proximity(self, groove, key_slot) -> bool:
        """检查挡圈槽与键槽的距离
        
        挡圈槽与键槽之间应有足够的距离以保证强度
        
        Args:
            groove: 挡圈槽要素
            key_slot: 键槽要素
        
        Returns:
            bool: 是否满足约束
        """
        min_distance = max(groove.m, key_slot.b) * 1.5

        return self.check_elements_proximity(groove, key_slot, min_distance)

    def check_nut_groove_proximity(self, nut_groove, other_element) -> bool:
        """检查圆螺母槽与相邻要素的距离
        
        Args:
            nut_groove: 圆螺母槽要素
            other_element: 相邻要素
        
        Returns:
            bool: 是否满足约束
        """
        min_distance = nut_groove.t_nut if hasattr(nut_groove, 't_nut') else 10.0

        return self.check_elements_proximity(nut_groove, other_element, min_distance)

    def check_all_elements(self, elements: List[object], shaft_length: float, 
                          shaft_radius: float) -> List[ConstraintViolation]:
        """批量检查所有要素的约束
        
        Args:
            elements: 要素列表
            shaft_length: 轴总长（mm）
            shaft_radius: 轴半径（mm）
        
        Returns:
            List[ConstraintViolation]: 所有约束违反记录
        """
        self.clear()

        for i, elem1 in enumerate(elements):
            if hasattr(elem1, 'validate'):
                elem1.validate()

            if hasattr(elem1, 'form') and elem1.form in ['A', 'C']:
                self.check_key_end_distance(elem1, shaft_length)

            if isinstance(elem1, DrillHole):
                self.check_drill_wall_thickness(elem1, shaft_radius)

            for j, elem2 in enumerate(elements):
                if i >= j:
                    continue

                self.check_element_overlap(elem1, elem2)

                if hasattr(elem1, 'form') and elem1.form in ['A', 'C']:
                    self.check_elements_proximity(elem1, elem2, 2.0)

        return self.violations

    def print_violations(self):
        """打印所有约束违反记录"""
        if not self.violations:
            print("[INFO] 所有约束检查通过")
            return

        errors = [v for v in self.violations if v.severity == "error"]
        warnings = [v for v in self.violations if v.severity == "warning"]

        if errors:
            print(f"\n[ERROR] 发现 {len(errors)} 个严重约束违反：")
            for v in errors:
                print(f"  - {v.message}")

        if warnings:
            print(f"\n[WARN] 发现 {len(warnings)} 个警告：")
            for v in warnings:
                print(f"  - {v.message}")

    def has_errors(self) -> bool:
        """是否存在严重约束违反"""
        return any(v.severity == "error" for v in self.violations)


def calculate_min_distance_between_elements(elem1, elem2) -> float:
    """计算两个要素之间的最小距离
    
    Args:
        elem1: 要素1（需有x_start, x_end属性）
        elem2: 要素2（需有x_start, x_end属性）
    
    Returns:
        float: 最小距离（mm），负数表示重叠
    """
    if not hasattr(elem1, 'x_start') or not hasattr(elem1, 'x_end'):
        return float('inf')
    if not hasattr(elem2, 'x_start') or not hasattr(elem2, 'x_end'):
        return float('inf')

    e1_start, e1_end = elem1.x_start, elem1.x_end
    e2_start, e2_end = elem2.x_start, elem2.x_end

    if e1_end < e2_start:
        return e2_start - e1_end
    elif e2_end < e1_start:
        return e1_start - e2_end
    else:
        return -(min(e1_end, e2_end) - max(e1_start, e2_start))


def create_drill_hole(x_center: float, y_center: float, diameter: float, 
                       depth: float = 10) -> DrillHole:
    """创建钻孔要素
    
    Args:
        x_center: 孔中心 X 坐标（mm）
        y_center: 孔中心 Y 坐标（mm），距轴心
        diameter: 孔径（mm）
        depth: 孔深（mm）
    
    Returns:
        DrillHole 实例
    """
    return DrillHole(x_center, y_center, diameter, depth)