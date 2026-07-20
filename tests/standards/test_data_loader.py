import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from standards.data_loader import (
    validate_data_files,
    load_gb_t1096,
    load_gb_t894,
    load_gb_t812,
    load_gb_t196,
    load_materials,
    load_sw_templates,
    get_flat_key_data,
    get_circlip_data,
    get_nut_data,
    get_nut_groove_data,
    get_thread_data,
    get_key_type_data,
    get_length_series,
    get_material_data,
    get_end_distance,
    clear_cache
)


def test_data_files():
    print('='*60)
    print('[测试1] 验证数据文件存在')
    print('='*60)
    
    result = validate_data_files()
    if result:
        print('[PASS] 所有数据文件存在')
    else:
        print('[FAIL] 数据文件缺失')
    return result


def test_load_gb_t1096():
    print('\n' + '='*60)
    print('[测试2] 加载 GB/T 1096 平键标准')
    print('='*60)
    
    data = load_gb_t1096()
    
    print(f"标准号: {data['standard']}")
    print(f"标题: {data['title']}")
    print(f"键类型数量: {len(data['key_types'])}")
    print(f"尺寸数据条目数: {len(data['dimensions'])}")
    print(f"键长系列数量: {len(data['length_series'])}")
    
    assert data['standard'] == 'GB/T 1096'
    assert len(data['key_types']) == 3
    assert len(data['dimensions']) > 40
    assert len(data['length_series']) == 26
    
    print('[PASS] GB/T 1096 加载成功')
    return True


def test_load_gb_t894():
    print('\n' + '='*60)
    print('[测试3] 加载 GB/T 894 弹性挡圈标准')
    print('='*60)
    
    data = load_gb_t894()
    
    print(f"标准号: {data['standard']}")
    print(f"标题: {data['title']}")
    print(f"尺寸数据条目数: {len(data['dimensions'])}")
    
    assert data['standard'] == 'GB/T 894.1'
    assert len(data['dimensions']) > 50
    
    print('[PASS] GB/T 894 加载成功')
    return True


def test_load_gb_t812():
    print('\n' + '='*60)
    print('[测试4] 加载 GB/T 812 圆螺母标准')
    print('='*60)
    
    data = load_gb_t812()
    
    print(f"标准号: {data['standard']}")
    print(f"标题: {data['title']}")
    print(f"尺寸数据条目数: {len(data['dimensions'])}")
    print(f"槽尺寸数据条目数: {len(data['groove_dimensions'])}")
    
    assert data['standard'] == 'GB/T 812'
    assert len(data['dimensions']) > 30
    assert len(data['groove_dimensions']) > 30
    
    print('[PASS] GB/T 812 加载成功')
    return True


def test_load_gb_t196():
    print('\n' + '='*60)
    print('[测试5] 加载 GB/T 196 螺纹标准')
    print('='*60)
    
    data = load_gb_t196()
    
    print(f"标准号: {data['standard']}")
    print(f"标题: {data['title']}")
    print(f"尺寸数据条目数: {len(data['dimensions'])}")
    
    assert data['standard'] == 'GB/T 196'
    assert len(data['dimensions']) > 30
    
    print('[PASS] GB/T 196 加载成功')
    return True


def test_load_materials():
    print('\n' + '='*60)
    print('[测试6] 加载材料属性')
    print('='*60)
    
    data = load_materials()
    
    print(f"类别: {data['category']}")
    print(f"材料数量: {len(data['materials'])}")
    
    assert data['category'] == 'steel'
    assert len(data['materials']) >= 5
    
    print('[PASS] 材料属性加载成功')
    return True


def test_load_sw_templates():
    print('\n' + '='*60)
    print('[测试7] 加载 SW 模板配置')
    print('='*60)
    
    data = load_sw_templates()
    
    print(f"版本: {data['version']}")
    print(f"搜索路径数量: {len(data['search_paths'])}")
    
    assert data['version'] == '1.0'
    assert len(data['search_paths']) > 0
    
    print('[PASS] SW 模板配置加载成功')
    return True


def test_get_flat_key_data():
    print('\n' + '='*60)
    print('[测试8] 获取平键尺寸数据')
    print('='*60)
    
    tests = [
        (30, {'b': 12, 'h': 8, 't1': 5.0, 't2': 3.3}),
        (40, {'b': 16, 'h': 10, 't1': 6.0, 't2': 4.3}),
        (50, {'b': 20, 'h': 12, 't1': 7.5, 't2': 4.9}),
    ]
    
    all_pass = True
    for diameter, expected in tests:
        data = get_flat_key_data(diameter)
        if data:
            for key, val in expected.items():
                if data.get(key) != val:
                    print(f"[FAIL] 轴径{diameter}mm: {key}不匹配, 期望={val}, 实际={data.get(key)}")
                    all_pass = False
            print(f"轴径{diameter}mm: b={data['b']}, h={data['h']}, t1={data['t1']}, t2={data['t2']}")
        else:
            print(f"[FAIL] 轴径{diameter}mm: 未找到数据")
            all_pass = False
    
    if all_pass:
        print('[PASS] 平键尺寸数据获取成功')
    return all_pass


def test_get_key_type_data():
    print('\n' + '='*60)
    print('[测试9] 获取键类型数据')
    print('='*60)
    
    key_types = ['A', 'B', 'C']
    
    for kt in key_types:
        data = get_key_type_data(kt)
        if data:
            print(f"类型{kt}: {data['name']}")
            assert data['type'] == kt
        else:
            print(f"[FAIL] 类型{kt}: 未找到数据")
            return False
    
    print('[PASS] 键类型数据获取成功')
    return True


def test_get_length_series():
    print('\n' + '='*60)
    print('[测试10] 获取键长系列')
    print('='*60)
    
    series = get_length_series()
    
    print(f"键长系列数量: {len(series)}")
    print(f"键长范围: {min(series)}~{max(series)}")
    
    assert len(series) == 26
    assert min(series) == 6
    assert max(series) == 160
    
    print('[PASS] 键长系列获取成功')
    return True


def test_get_end_distance():
    print('\n' + '='*60)
    print('[测试11] 获取键槽与轴端面距离')
    print('='*60)
    
    tests = [
        (20, 5),
        (35, 8),
        (60, 10),
        (90, 15),
    ]
    
    all_pass = True
    for diameter, expected_min in tests:
        data = get_end_distance(diameter)
        if data and data['min'] == expected_min:
            print(f"轴径{diameter}mm: 最小距离={data['min']}, 推荐距离={data['recommend']}")
        else:
            print(f"[FAIL] 轴径{diameter}mm: 期望最小距离={expected_min}, 实际={data.get('min') if data else 'None'}")
            all_pass = False
    
    if all_pass:
        print('[PASS] 键槽与轴端面距离获取成功')
    return all_pass


def test_get_material_data():
    print('\n' + '='*60)
    print('[测试12] 获取材料属性数据')
    print('='*60)
    
    materials = ['45', '40Cr', 'Q235']
    
    all_pass = True
    for mat in materials:
        data = get_material_data(mat)
        if data:
            print(f"{mat}: {data['name']}, 弹性模量={data['elastic_modulus']}MPa")
        else:
            print(f"[FAIL] {mat}: 未找到数据")
            all_pass = False
    
    if all_pass:
        print('[PASS] 材料属性数据获取成功')
    return all_pass


def test_get_thread_data():
    print('\n' + '='*60)
    print('[测试13] 获取螺纹尺寸数据')
    print('='*60)
    
    threads = ['M20', 'M30', 'M40', 'M50']
    
    all_pass = True
    for thread in threads:
        data = get_thread_data(thread)
        if data:
            print(f"{thread}: 螺距={data['pitch']}, 小径={data['d1']}")
        else:
            print(f"[FAIL] {thread}: 未找到数据")
            all_pass = False
    
    if all_pass:
        print('[PASS] 螺纹尺寸数据获取成功')
    return all_pass


def run_all_tests():
    print('='*60)
    print('数据加载器测试')
    print('='*60)
    
    tests = [
        test_data_files,
        test_load_gb_t1096,
        test_load_gb_t894,
        test_load_gb_t812,
        test_load_gb_t196,
        test_load_materials,
        test_load_sw_templates,
        test_get_flat_key_data,
        test_get_key_type_data,
        test_get_length_series,
        test_get_end_distance,
        test_get_material_data,
        test_get_thread_data,
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
    
    clear_cache()
    return passed == total


if __name__ == '__main__':
    sys.exit(0 if run_all_tests() else 1)