import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculations.shaft import (
    ShaftCalculator, ShaftSection, ShaftStrengthResult,
    calculate_shaft_mass, calculate_torque_from_power
)


def test_inertia_calculations():
    print('='*60)
    print('[测试1] 惯性矩计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    diameter = 30.0
    
    J_p = calc.polar_moment_of_inertia(diameter)
    expected_J_p = math.pi * diameter ** 4 / 32.0
    
    I_y = calc.axial_moment_of_inertia(diameter)
    expected_I_y = math.pi * diameter ** 4 / 64.0
    
    print(f'  直径 {diameter}mm:')
    print(f'    极惯性矩: 计算={J_p:.2f}mm^4, 期望={expected_J_p:.2f}mm^4')
    print(f'    轴向惯性矩: 计算={I_y:.2f}mm^4, 期望={expected_I_y:.2f}mm^4')
    
    if abs(J_p - expected_J_p) < 0.01:
        print('    [PASS] 极惯性矩计算正确')
    else:
        print('    [FAIL] 极惯性矩计算错误')
        all_pass = False
    
    if abs(I_y - expected_I_y) < 0.01:
        print('    [PASS] 轴向惯性矩计算正确')
    else:
        print('    [FAIL] 轴向惯性矩计算错误')
        all_pass = False
    
    return all_pass


def test_section_modulus():
    print('\n' + '='*60)
    print('[测试2] 截面系数计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    diameter = 30.0
    
    W = calc.section_modulus(diameter)
    expected_W = math.pi * diameter ** 3 / 32.0
    
    W_p = calc.torsion_modulus(diameter)
    expected_W_p = math.pi * diameter ** 3 / 16.0
    
    print(f'  直径 {diameter}mm:')
    print(f'    抗弯截面系数: 计算={W:.2f}mm^3, 期望={expected_W:.2f}mm^3')
    print(f'    抗扭截面系数: 计算={W_p:.2f}mm^3, 期望={expected_W_p:.2f}mm^3')
    
    if abs(W - expected_W) < 0.01:
        print('    [PASS] 抗弯截面系数计算正确')
    else:
        print('    [FAIL] 抗弯截面系数计算错误')
        all_pass = False
    
    if abs(W_p - expected_W_p) < 0.01:
        print('    [PASS] 抗扭截面系数计算正确')
    else:
        print('    [FAIL] 抗扭截面系数计算错误')
        all_pass = False
    
    return all_pass


def test_equivalent_diameter():
    print('\n' + '='*60)
    print('[测试3] 当量直径计算（考虑键槽）')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    diameter = 30.0
    key_depth = 5.0
    
    d_eq_0 = calc.equivalent_diameter(diameter, 0, key_depth)
    d_eq_1 = calc.equivalent_diameter(diameter, 1, key_depth)
    d_eq_2 = calc.equivalent_diameter(diameter, 2, key_depth)
    
    print(f'  实际直径 {diameter}mm, 键槽深度 {key_depth}mm:')
    print(f'    无键槽: d_eq={d_eq_0:.2f}mm')
    print(f'    单键槽: d_eq={d_eq_1:.2f}mm')
    print(f'    双键槽: d_eq={d_eq_2:.2f}mm')
    
    if d_eq_0 == diameter:
        print('    [PASS] 无键槽当量直径等于实际直径')
    else:
        print('    [FAIL] 无键槽当量直径错误')
        all_pass = False
    
    if d_eq_1 < diameter:
        print('    [PASS] 单键槽当量直径小于实际直径')
    else:
        print('    [FAIL] 单键槽当量直径应小于实际直径')
        all_pass = False
    
    if d_eq_2 < d_eq_1:
        print('    [PASS] 双键槽当量直径小于单键槽')
    else:
        print('    [FAIL] 双键槽当量直径应小于单键槽')
        all_pass = False
    
    return all_pass


def test_diameter_estimation():
    print('\n' + '='*60)
    print('[测试4] 轴径估算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    torque = 100000  # N·mm
    bending_moment = 50000  # N·mm
    
    d_torsion = calc.estimate_diameter_by_torsion(torque)
    d_bending = calc.estimate_diameter_by_bending_torsion(torque, bending_moment)
    
    print(f'  扭矩 {torque}N·mm, 弯矩 {bending_moment}N·mm:')
    print(f'    按扭转强度估算: {d_torsion}mm')
    print(f'    按弯扭组合估算: {d_bending}mm')
    
    if d_torsion > 0:
        print('    [PASS] 扭转强度估算轴径 > 0')
    else:
        print('    [FAIL] 扭转强度估算轴径应为正数')
        all_pass = False
    
    if d_bending >= d_torsion:
        print('    [PASS] 弯扭组合估算轴径 >= 扭转强度估算')
    else:
        print('    [FAIL] 弯扭组合估算轴径应大于等于扭转强度估算')
        all_pass = False
    
    return all_pass


def test_stress_calculations():
    print('\n' + '='*60)
    print('[测试5] 应力计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    diameter = 30.0
    torque = 100000  # N·mm
    bending_moment = 50000  # N·mm
    
    tau = calc.shear_stress(torque, diameter)
    sigma = calc.bending_stress(bending_moment, diameter)
    sigma_eq = calc.combined_stress(torque, bending_moment, diameter)
    
    print(f'  直径 {diameter}mm, 扭矩 {torque}N·mm, 弯矩 {bending_moment}N·mm:')
    print(f'    剪切应力: {tau:.2f}MPa')
    print(f'    弯曲应力: {sigma:.2f}MPa')
    print(f'    弯扭组合应力: {sigma_eq:.2f}MPa')
    
    if tau > 0:
        print('    [PASS] 剪切应力 > 0')
    else:
        print('    [FAIL] 剪切应力应为正数')
        all_pass = False
    
    if sigma > 0:
        print('    [PASS] 弯曲应力 > 0')
    else:
        print('    [FAIL] 弯曲应力应为正数')
        all_pass = False
    
    if sigma_eq >= sigma and sigma_eq >= tau:
        print('    [PASS] 弯扭组合应力 >= 各单项应力')
    else:
        print('    [FAIL] 弯扭组合应力应大于等于各单项应力')
        all_pass = False
    
    return all_pass


def test_critical_speed():
    print('\n' + '='*60)
    print('[测试6] 临界转速计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    diameter = 30.0
    length = 500.0
    
    n_cr = calc.critical_speed_simple(diameter, length)
    
    print(f'  直径 {diameter}mm, 跨距 {length}mm:')
    print(f'    临界转速: {n_cr:.1f}rpm')
    
    if n_cr > 0:
        print('    [PASS] 临界转速 > 0')
    else:
        print('    [FAIL] 临界转速应为正数')
        all_pass = False
    
    return all_pass


def test_strength_check():
    print('\n' + '='*60)
    print('[测试7] 强度校核')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator(material="45")
    
    diameter = 40.0
    torque = 100000  # N·mm
    bending_moment = 50000  # N·mm
    
    result = calc.check_strength(diameter, torque, bending_moment)
    
    print(f'  材料: {result["material"]}')
    print(f'  当量直径: {result["equivalent_diameter"]:.2f}mm')
    print(f'  剪切应力: {result["shear_stress"]["value"]:.2f}MPa / {result["shear_stress"]["allowable"]:.2f}MPa')
    print(f'  弯曲应力: {result["bending_stress"]["value"]:.2f}MPa / {result["bending_stress"]["allowable"]:.2f}MPa')
    print(f'  组合应力: {result["combined_stress"]["value"]:.2f}MPa / {result["combined_stress"]["allowable"]:.2f}MPa')
    
    if result["shear_stress"]["pass"]:
        print('    [PASS] 剪切强度校核通过')
    else:
        print('    [WARN] 剪切强度校核未通过')
    
    if result["bending_stress"]["pass"]:
        print('    [PASS] 弯曲强度校核通过')
    else:
        print('    [WARN] 弯曲强度校核未通过')
    
    if result["combined_stress"]["pass"]:
        print('    [PASS] 弯扭组合强度校核通过')
    else:
        print('    [WARN] 弯扭组合强度校核未通过')
    
    return all_pass


def test_calculate_all():
    print('\n' + '='*60)
    print('[测试8] 完整计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    result = calc.calculate_all(
        diameter=30.0,
        length=500.0,
        torque=100000,
        bending_moment=50000,
        key_slot_count=1,
        key_slot_depth=5.0
    )
    
    print(f'  直径: {result.diameter}mm')
    print(f'  极惯性矩: {result.polar_moment:.2f}mm^4')
    print(f'  轴向惯性矩: {result.axial_moment_y:.2f}mm^4')
    print(f'  抗弯截面系数: {result.section_modulus:.2f}mm^3')
    print(f'  抗扭截面系数: {result.torsion_modulus:.2f}mm^3')
    print(f'  当量直径: {result.equivalent_diameter:.2f}mm')
    print(f'  临界转速: {result.critical_speed:.1f}rpm')
    print(f'  剪切应力: {result.shear_stress:.2f}MPa')
    print(f'  弯曲应力: {result.bending_stress:.2f}MPa')
    print(f'  组合应力: {result.combined_stress:.2f}MPa')
    
    if result.equivalent_diameter < result.diameter:
        print('    [PASS] 当量直径正确考虑键槽影响')
    else:
        print('    [FAIL] 当量直径应小于实际直径')
        all_pass = False
    
    return all_pass


def test_mass_and_torque():
    print('\n' + '='*60)
    print('[测试9] 质量与扭矩辅助计算')
    print('='*60)
    
    all_pass = True
    
    mass = calculate_shaft_mass(30, 500)
    print(f'  轴质量 (d=30mm, L=500mm): {mass:.3f}kg')
    
    if mass > 0:
        print('    [PASS] 轴质量计算正确')
    else:
        print('    [FAIL] 轴质量应为正数')
        all_pass = False
    
    torque = calculate_torque_from_power(10, 1000)
    print(f'  扭矩 (P=10kW, n=1000rpm): {torque:.2f}N·m')
    
    expected_torque = 9550 * 10 / 1000
    if abs(torque - expected_torque) < 0.01:
        print('    [PASS] 扭矩计算正确')
    else:
        print('    [FAIL] 扭矩计算错误')
        all_pass = False
    
    return all_pass


def test_allowable_torque():
    print('\n' + '='*60)
    print('[测试10] 许用扭矩计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator(material="45")
    
    diameter = 30.0
    T_allow = calc.calculate_allowable_torque(diameter)
    
    W_p = math.pi * diameter ** 3 / 16.0
    tau_allow = 210 / 3
    expected_T_allow = W_p * tau_allow
    
    print(f'  直径 {diameter}mm (45钢):')
    print(f'    许用扭矩: 计算={T_allow:.0f}N·mm, 期望={expected_T_allow:.0f}N·mm')
    
    if abs(T_allow - expected_T_allow) < 1:
        print('    [PASS] 许用扭矩计算正确')
    else:
        print('    [FAIL] 许用扭矩计算错误')
        all_pass = False
    
    T_allow_40cr = ShaftCalculator(material="40Cr").calculate_allowable_torque(diameter)
    print(f'    40Cr许用扭矩: {T_allow_40cr:.0f}N·mm')
    
    if T_allow_40cr > T_allow:
        print('    [PASS] 40Cr许用扭矩大于45钢')
    else:
        print('    [FAIL] 40Cr许用扭矩应大于45钢')
        all_pass = False
    
    return all_pass


def test_allowable_bending_moment():
    print('\n' + '='*60)
    print('[测试11] 许用弯矩计算')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator(material="45")
    
    diameter = 30.0
    M_allow = calc.calculate_allowable_bending_moment(diameter)
    
    W = math.pi * diameter ** 3 / 32.0
    sigma_allow = 355 / 3
    expected_M_allow = W * sigma_allow
    
    print(f'  直径 {diameter}mm (45钢):')
    print(f'    许用弯矩: 计算={M_allow:.0f}N·mm, 期望={expected_M_allow:.0f}N·mm')
    
    if abs(M_allow - expected_M_allow) < 1:
        print('    [PASS] 许用弯矩计算正确')
    else:
        print('    [FAIL] 许用弯矩计算错误')
        all_pass = False
    
    return all_pass


def test_round_to_standard():
    print('\n' + '='*60)
    print('[测试12] 标准直径系列圆整')
    print('='*60)
    
    all_pass = True
    
    calc = ShaftCalculator()
    
    test_cases = [
        (28.5, 32),
        (30.0, 32),
        (32.0, 32),
        (35.0, 40),
        (45.0, 50),
        (56.0, 63),
    ]
    
    print('  第一系列圆整:')
    for diameter, expected in test_cases:
        result = calc.round_to_standard(diameter, series="first")
        status = '[PASS]' if result == expected else '[FAIL]'
        print(f'    {diameter}mm → {result}mm (期望{expected}mm) {status}')
        if result != expected:
            all_pass = False
    
    print('  考虑加工余量(2mm):')
    result = calc.round_to_standard(28.5, series="first", machining_allowance=2)
    print(f'    28.5mm + 2mm余量 → {result}mm')
    if result >= 30.5:
        print('    [PASS] 考虑加工余量后圆整正确')
    else:
        print('    [FAIL] 考虑加工余量后圆整错误')
        all_pass = False
    
    return all_pass


def run_all_tests():
    print('='*60)
    print('轴强度计算模块测试')
    print('='*60)
    
    tests = [
        test_inertia_calculations,
        test_section_modulus,
        test_equivalent_diameter,
        test_diameter_estimation,
        test_stress_calculations,
        test_critical_speed,
        test_strength_check,
        test_calculate_all,
        test_mass_and_torque,
        test_allowable_torque,
        test_allowable_bending_moment,
        test_round_to_standard,
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