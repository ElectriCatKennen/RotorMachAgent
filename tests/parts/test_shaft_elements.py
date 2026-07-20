import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parts.shaft_elements import (
    KeySlot, CirclipGroove, Thread, NutGroove,
    create_key_slot, create_circlip_groove, create_thread, create_nut_groove
)


def test_key_slot_a_type():
    print('='*60)
    print('[测试1] A型平键槽要素（圆头）')
    print('='*60)
    
    all_pass = True
    
    key_slot = create_key_slot(x_center=50, length=50, diameter=30, form='A')
    
    print(f'\n轴径 30mm A型键槽:')
    print(f'  标准尺寸 - 键宽b={key_slot.b}, 键高h={key_slot.h}, 轴槽深t1={key_slot.t1}')
    print(f'  圆弧参数 - 圆弧半径={key_slot.arc_radius}, 圆弧半径比={key_slot.arc_radius_ratio}')
    print(f'  几何参数 - x_start={key_slot.x_start}, x_end={key_slot.x_end}')
    print(f'  几何参数 - y_bottom={key_slot.y_bottom}, y_top={key_slot.y_top}')
    print(f'  左圆弧中心: {key_slot.arc_center_left}')
    print(f'  右圆弧中心: {key_slot.arc_center_right}')
    print(f'  键长约束: {key_slot.length_constraint}')
    print(f'  最小键长: {key_slot.get_min_length()}mm')
    
    if key_slot.b == 12 and key_slot.h == 8 and key_slot.t1 == 5.0:
        print('  [PASS] 尺寸匹配标准 GB/T 1096')
    else:
        print('  [FAIL] 尺寸不匹配标准')
        all_pass = False
    
    if key_slot.arc_radius == 6.0:
        print('  [PASS] 圆弧半径正确')
    else:
        print('  [FAIL] 圆弧半径错误')
        all_pass = False
    
    if key_slot.get_min_length() == 12.0:
        print('  [PASS] 最小键长计算正确')
    else:
        print('  [FAIL] 最小键长计算错误')
        all_pass = False
    
    if key_slot.validate():
        print('  [PASS] 参数验证通过')
    else:
        print('  [FAIL] 参数验证失败')
        all_pass = False
    
    return all_pass


def test_key_slot_c_type():
    print('\n' + '='*60)
    print('[测试2] C型平键槽要素（单圆头）')
    print('='*60)
    
    all_pass = True
    
    key_slot = create_key_slot(x_center=50, length=50, diameter=30, form='C')
    
    print(f'\n轴径 30mm C型键槽:')
    print(f'  标准尺寸 - 键宽b={key_slot.b}, 键高h={key_slot.h}, 轴槽深t1={key_slot.t1}')
    print(f'  圆弧参数 - 圆弧半径={key_slot.arc_radius}, 需要压板={key_slot.requires_plate}')
    print(f'  几何参数 - x_start={key_slot.x_start}, x_end={key_slot.x_end}')
    print(f'  最小键长: {key_slot.get_min_length()}mm')
    
    if key_slot.b == 12 and key_slot.h == 8 and key_slot.t1 == 5.0:
        print('  [PASS] 尺寸匹配标准 GB/T 1096')
    else:
        print('  [FAIL] 尺寸不匹配标准')
        all_pass = False
    
    if key_slot.arc_radius == 6.0:
        print('  [PASS] 圆弧半径正确')
    else:
        print('  [FAIL] 圆弧半径错误')
        all_pass = False
    
    if key_slot.requires_plate:
        print('  [PASS] C型键需要压板标志正确')
    else:
        print('  [FAIL] C型键需要压板标志错误')
        all_pass = False
    
    if key_slot.get_min_length() == 6.0:
        print('  [PASS] 最小键长计算正确（C型为圆弧半径）')
    else:
        print('  [FAIL] 最小键长计算错误')
        all_pass = False
    
    return all_pass


def test_key_slot_b_type():
    print('\n' + '='*60)
    print('[测试3] B型平键槽要素（平头）')
    print('='*60)
    
    all_pass = True
    
    key_slot = create_key_slot(x_center=50, length=50, diameter=30, form='B')
    
    print(f'\n轴径 30mm B型键槽:')
    print(f'  标准尺寸 - 键宽b={key_slot.b}, 键高h={key_slot.h}, 轴槽深t1={key_slot.t1}')
    print(f'  圆弧参数 - 圆弧半径={key_slot.arc_radius}')
    print(f'  几何参数 - x_start={key_slot.x_start}, x_end={key_slot.x_end}')
    print(f'  最小键长: {key_slot.get_min_length()}mm')
    
    if key_slot.b == 12 and key_slot.h == 8 and key_slot.t1 == 5.0:
        print('  [PASS] 尺寸匹配标准 GB/T 1096')
    else:
        print('  [FAIL] 尺寸不匹配标准')
        all_pass = False
    
    if key_slot.arc_radius == 0:
        print('  [PASS] B型键无圆弧')
    else:
        print('  [FAIL] B型键不应有圆弧')
        all_pass = False
    
    if key_slot.get_min_length() == 12.0:
        print('  [PASS] 最小键长等于键宽')
    else:
        print('  [FAIL] 最小键长计算错误')
        all_pass = False
    
    return all_pass


def test_key_length_validation():
    print('\n' + '='*60)
    print('[测试4] 键长标准系列验证')
    print('='*60)
    
    all_pass = True
    
    valid_lengths = [25, 32, 40, 50]
    invalid_lengths = [23, 31, 39, 51]
    
    print('\n有效键长测试:')
    for length in valid_lengths:
        key_slot = create_key_slot(x_center=50, length=length, diameter=30)
        if key_slot.is_length_valid():
            print(f'  [PASS] 键长 {length}mm 符合标准系列')
        else:
            print(f'  [FAIL] 键长 {length}mm 验证失败')
            all_pass = False
    
    print('\n无效键长测试:')
    for length in invalid_lengths:
        key_slot = create_key_slot(x_center=50, length=length, diameter=30)
        if not key_slot.is_length_valid():
            print(f'  [PASS] 键长 {length}mm 被正确拒绝')
        else:
            print(f'  [FAIL] 键长 {length}mm 应该被拒绝')
            all_pass = False
    
    print('\n键长小于圆弧约束测试:')
    key_slot = create_key_slot(x_center=50, length=10, diameter=30, form='A')
    if not key_slot.is_length_valid():
        print(f'  [PASS] A型键长 10mm < 最小 12mm 被正确拒绝')
    else:
        print(f'  [FAIL] A型键长 10mm 应该被拒绝')
        all_pass = False
    
    return all_pass


def test_key_end_distance():
    print('\n' + '='*60)
    print('[测试5] 键槽与轴端面距离要求')
    print('='*60)
    
    all_pass = True
    
    tests = [
        (20, 5),
        (35, 8),
        (60, 10),
        (90, 15),
    ]
    
    for diameter, expected_min in tests:
        key_slot = create_key_slot(x_center=50, length=50, diameter=diameter)
        dist_req = key_slot.get_end_distance_requirement()
        if dist_req and dist_req['min'] == expected_min:
            print(f'  [PASS] 轴径{diameter}mm: 最小距离={dist_req["min"]}, 推荐={dist_req["recommend"]}')
        else:
            print(f'  [FAIL] 轴径{diameter}mm: 期望最小距离={expected_min}, 实际={dist_req.get("min") if dist_req else "None"}')
            all_pass = False
    
    return all_pass


def test_circlip_groove():
    print('\n' + '='*60)
    print('[测试6] 挡圈槽要素（GB/T 894）')
    print('='*60)
    
    all_pass = True
    
    diameters = [30, 40, 50]
    
    for diameter in diameters:
        groove = create_circlip_groove(x_center=50, diameter=diameter)
        
        print(f'\n轴径 {diameter}mm 挡圈槽:')
        print(f'  标准尺寸 - 槽宽m={groove.m}, 槽深n={groove.n}, 槽底直径d1={groove.d1}')
        print(f'  几何参数 - x_start={groove.x_start}, x_end={groove.x_end}')
        print(f'  几何参数 - y_bottom={groove.y_bottom}, y_top={groove.y_top}')
        
        if groove.m > 0:
            print('  [PASS] 尺寸匹配标准 GB/T 894')
        else:
            print('  [FAIL] 尺寸不匹配标准')
            all_pass = False
        
        if groove.validate():
            print('  [PASS] 参数验证通过')
        else:
            print('  [FAIL] 参数验证失败')
            all_pass = False
    
    return all_pass


def test_thread():
    print('\n' + '='*60)
    print('[测试7] 螺纹要素（GB/T 196）')
    print('='*60)
    
    all_pass = True
    
    threads = ['M20', 'M30', 'M40']
    
    for thread_name in threads:
        diameter = int(thread_name[1:])
        thread = create_thread(x_start=100, length=30, diameter=diameter)
        
        print(f'\n{thread_name} 螺纹:')
        print(f'  标准尺寸 - 螺距={thread.pitch}, 小径d1={thread.d1}, 中径d2={thread.d2}')
        print(f'  几何参数 - x_start={thread.x_start}, x_end={thread.x_end}')
        
        if thread.pitch > 0 and thread.d1 > 0:
            print('  [PASS] 尺寸匹配标准 GB/T 196')
        else:
            print('  [FAIL] 尺寸不匹配标准')
            all_pass = False
    
    return all_pass


def test_nut_groove():
    print('\n' + '='*60)
    print('[测试8] 圆螺母槽要素（GB/T 812）')
    print('='*60)
    
    all_pass = True
    
    nuts = ['M20', 'M30', 'M40']
    
    for nut_name in nuts:
        diameter = int(nut_name[1:])
        groove = create_nut_groove(x_center=50, diameter=diameter)
        
        print(f'\n{nut_name} 圆螺母槽:')
        print(f'  标准尺寸 - 槽宽m={groove.m}, 槽深n={groove.n}')
        print(f'  螺母参数 - 外径D={groove.D_nut}, 厚度t={groove.t_nut}')
        print(f'  几何参数 - x_start={groove.x_start}, x_end={groove.x_end}')
        
        if groove.m > 0:
            print('  [PASS] 尺寸匹配标准 GB/T 812')
        else:
            print('  [FAIL] 尺寸不匹配标准')
            all_pass = False
        
        if groove.validate():
            print('  [PASS] 参数验证通过')
        else:
            print('  [FAIL] 参数验证失败')
            all_pass = False
    
    return all_pass


def test_geometry_calculations():
    print('\n' + '='*60)
    print('[测试9] 几何参数计算')
    print('='*60)
    
    all_pass = True
    
    key_slot = create_key_slot(x_center=50, length=50, diameter=30, form='A')
    expected_x_start = 31.0
    expected_x_end = 69.0
    expected_y_bottom = 10.0
    expected_y_top = 15.0
    
    print(f'\n键槽几何计算 (A型，含圆弧):')
    print(f'  x_start: 期望={expected_x_start}, 实际={key_slot.x_start}')
    print(f'  x_end: 期望={expected_x_end}, 实际={key_slot.x_end}')
    print(f'  y_bottom: 期望={expected_y_bottom}, 实际={key_slot.y_bottom}')
    print(f'  y_top: 期望={expected_y_top}, 实际={key_slot.y_top}')
    
    if (abs(key_slot.x_start - expected_x_start) < 0.01 and
        abs(key_slot.x_end - expected_x_end) < 0.01 and
        abs(key_slot.y_bottom - expected_y_bottom) < 0.01 and
        abs(key_slot.y_top - expected_y_top) < 0.01):
        print('  [PASS] A型键槽几何计算正确')
    else:
        print('  [FAIL] A型键槽几何计算错误')
        all_pass = False
    
    key_slot_b = create_key_slot(x_center=50, length=50, diameter=30, form='B')
    expected_x_start_b = 25.0
    expected_x_end_b = 75.0
    
    print(f'\n键槽几何计算 (B型，无圆弧):')
    print(f'  x_start: 期望={expected_x_start_b}, 实际={key_slot_b.x_start}')
    print(f'  x_end: 期望={expected_x_end_b}, 实际={key_slot_b.x_end}')
    
    if (abs(key_slot_b.x_start - expected_x_start_b) < 0.01 and
        abs(key_slot_b.x_end - expected_x_end_b) < 0.01):
        print('  [PASS] B型键槽几何计算正确')
    else:
        print('  [FAIL] B型键槽几何计算错误')
        all_pass = False
    
    groove = create_circlip_groove(x_center=50, diameter=30)
    print(f'\n挡圈槽几何计算:')
    print(f'  x_start: {groove.x_start}, x_end: {groove.x_end}')
    
    if abs(groove.x_end - groove.x_start - groove.m) < 0.01:
        print('  [PASS] 挡圈槽几何计算正确')
    else:
        print('  [FAIL] 挡圈槽几何计算错误')
        all_pass = False
    
    return all_pass


def run_all_tests():
    print('='*60)
    print('轴要素元类体系测试')
    print('='*60)
    
    tests = [
        test_key_slot_a_type,
        test_key_slot_c_type,
        test_key_slot_b_type,
        test_key_length_validation,
        test_key_end_distance,
        test_circlip_groove,
        test_thread,
        test_nut_groove,
        test_geometry_calculations,
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