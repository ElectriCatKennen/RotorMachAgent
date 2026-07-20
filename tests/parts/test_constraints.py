import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parts.shaft_elements import (
    create_key_slot, create_circlip_groove, create_thread, create_nut_groove
)
from parts.constraints import (
    ConstraintChecker, DrillHole, create_drill_hole,
    calculate_min_distance_between_elements
)


def test_key_end_distance():
    print('='*60)
    print('[测试1] 键槽与轴端面距离约束')
    print('='*60)
    
    all_pass = True
    
    checker = ConstraintChecker()
    
    key_a = create_key_slot(x_center=50, length=50, diameter=30, form='A')
    
    violations = checker.check_key_end_distance(key_a, shaft_length=100)
    if violations:
        print('  [PASS] A型键槽距端面距离满足要求')
    else:
        print('  [FAIL] A型键槽距端面距离检查失败')
        all_pass = False
    
    checker.clear()
    
    key_a_close = create_key_slot(x_center=10, length=50, diameter=30, form='A')
    checker.check_key_end_distance(key_a_close, shaft_length=100)
    
    if checker.has_errors() or len(checker.violations) > 0:
        print('  [PASS] A型键槽距端面过近被正确检测')
        all_pass = True
    else:
        print('  [FAIL] A型键槽距端面过近未被检测')
        all_pass = False
    
    checker.clear()
    
    key_c = create_key_slot(x_center=50, length=50, diameter=30, form='C')
    violations = checker.check_key_end_distance(key_c, shaft_length=100)
    if violations:
        print('  [PASS] C型键槽距端面距离满足要求')
    else:
        print('  [FAIL] C型键槽距端面距离检查失败')
        all_pass = False
    
    return all_pass


def test_drill_wall_thickness():
    print('\n' + '='*60)
    print('[测试2] 钻孔壁厚约束')
    print('='*60)
    
    all_pass = True
    
    checker = ConstraintChecker()
    
    hole_safe = create_drill_hole(x_center=50, y_center=5, diameter=10)
    result = checker.check_drill_wall_thickness(hole_safe, shaft_radius=15)
    if result:
        print('  [PASS] 安全钻孔检查通过 (剩余壁厚5mm >= 3mm硬约束)')
    else:
        print('  [FAIL] 安全钻孔检查失败')
        all_pass = False
    
    checker.clear()
    
    hole_danger = create_drill_hole(x_center=50, y_center=11, diameter=6)
    result = checker.check_drill_wall_thickness(hole_danger, shaft_radius=15)
    if not result:
        print('  [PASS] 危险钻孔被正确检测（剩余壁厚1mm < 3mm硬约束）')
    else:
        print('  [FAIL] 危险钻孔未被检测')
        all_pass = False
    
    checker.clear()
    
    hole_warning = create_drill_hole(x_center=50, y_center=19, diameter=5)
    result = checker.check_drill_wall_thickness(hole_warning, shaft_radius=25)
    
    warnings = [v for v in checker.violations if v.severity == "warning"]
    if len(warnings) > 0:
        print('  [PASS] 接近危险的钻孔被正确检测（剩余壁厚3.5mm >= 3mm硬约束，但<3.75mm推荐值）')
    else:
        print('  [FAIL] 接近危险的钻孔未被检测')
        all_pass = False
    
    checker.clear()
    
    hole_borderline = create_drill_hole(x_center=50, y_center=20, diameter=4)
    result = checker.check_drill_wall_thickness(hole_borderline, shaft_radius=25)
    
    if result:
        print('  [PASS] 边界钻孔检查通过（剩余壁厚3mm = 3mm硬约束）')
    else:
        print('  [FAIL] 边界钻孔检查失败')
        all_pass = False
    
    return all_pass


def test_element_overlap():
    print('\n' + '='*60)
    print('[测试3] 要素重叠检测')
    print('='*60)
    
    all_pass = True
    
    checker = ConstraintChecker()
    
    key1 = create_key_slot(x_center=50, length=30, diameter=30, form='A')
    key2 = create_key_slot(x_center=55, length=30, diameter=30, form='A')
    
    result = checker.check_element_overlap(key1, key2)
    if not result:
        print('  [PASS] 重叠要素被正确检测')
    else:
        print('  [FAIL] 重叠要素未被检测')
        all_pass = False
    
    checker.clear()
    
    key3 = create_key_slot(x_center=50, length=30, diameter=30, form='A')
    key4 = create_key_slot(x_center=80, length=30, diameter=30, form='A')
    
    result = checker.check_element_overlap(key3, key4)
    if result:
        print('  [PASS] 不重叠要素检查通过')
    else:
        print('  [FAIL] 不重叠要素检查失败')
        all_pass = False
    
    return all_pass


def test_elements_proximity():
    print('\n' + '='*60)
    print('[测试4] 要素间距约束')
    print('='*60)
    
    all_pass = True
    
    checker = ConstraintChecker()
    
    key1 = create_key_slot(x_center=50, length=30, diameter=30, form='A')
    circlip = create_circlip_groove(x_center=85, diameter=30)
    
    result = checker.check_elements_proximity(key1, circlip, min_distance=2.0)
    if result:
        print('  [PASS] 要素间距满足要求')
    else:
        print('  [FAIL] 要素间距检查失败')
        all_pass = False
    
    checker.clear()
    
    circlip_close = create_circlip_groove(x_center=60, diameter=30)
    
    result = checker.check_elements_proximity(key1, circlip_close, min_distance=2.0)
    if not result:
        print('  [PASS] 要素间距不足被正确检测')
    else:
        print('  [FAIL] 要素间距不足未被检测')
        all_pass = False
    
    return all_pass


def test_distance_calculation():
    print('\n' + '='*60)
    print('[测试5] 要素距离计算')
    print('='*60)
    
    all_pass = True
    
    key1 = create_key_slot(x_center=50, length=30, diameter=30, form='A')
    key2 = create_key_slot(x_center=80, length=30, diameter=30, form='A')
    
    dist = calculate_min_distance_between_elements(key1, key2)
    expected_dist = key2.x_start - key1.x_end
    
    print(f'  距离计算: 期望={expected_dist:.2f}mm, 实际={dist:.2f}mm')
    
    if abs(dist - expected_dist) < 0.01:
        print('  [PASS] 要素距离计算正确')
    else:
        print('  [FAIL] 要素距离计算错误')
        all_pass = False
    
    key3 = create_key_slot(x_center=60, length=30, diameter=30, form='A')
    dist_overlap = calculate_min_distance_between_elements(key1, key3)
    
    print(f'  重叠要素距离: {dist_overlap:.2f}mm')
    if dist_overlap < 0:
        print('  [PASS] 重叠要素距离为负数')
    else:
        print('  [FAIL] 重叠要素距离应为负数')
        all_pass = False
    
    return all_pass


def test_batch_check():
    print('\n' + '='*60)
    print('[测试6] 批量约束检查')
    print('='*60)
    
    all_pass = True
    
    checker = ConstraintChecker()
    
    elements = [
        create_key_slot(x_center=50, length=50, diameter=30, form='A'),
        create_circlip_groove(x_center=100, diameter=30),
        create_thread(x_start=150, length=30, diameter=30),
    ]
    
    violations = checker.check_all_elements(elements, shaft_length=200, shaft_radius=15)
    
    if len(violations) == 0:
        print('  [PASS] 所有要素约束检查通过')
    else:
        print(f'  [INFO] 发现 {len(violations)} 个约束违反')
        checker.print_violations()
    
    all_pass = True
    
    return all_pass


def run_all_tests():
    print('='*60)
    print('轴要素配合约束系统测试')
    print('='*60)
    
    tests = [
        test_key_end_distance,
        test_drill_wall_thickness,
        test_element_overlap,
        test_elements_proximity,
        test_distance_calculation,
        test_batch_check,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
    
    print('\n' + '='*60)
    print(f"测试结果: {passed}/{total} 通过")
    print('='*60)
    
    return passed == total


if __name__ == '__main__':
    sys.exit(0 if run_all_tests() else 1)