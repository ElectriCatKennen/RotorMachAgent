"""SolidWorksAdapter 单步指令验收测试

验证所有单步指令方法的基本可用性，确保每个方法独立运行不出错。

测试步骤：
1. 启动 SW
2. 新建零件
3. 草图操作（基础绘图）
4. 特征操作（拉伸凸台/旋转凸台/拉伸切除/旋转切除）
5. 特征树遍历
6. 保存并退出
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import time
import math

from adapters.solidworks import SolidWorksAdapter
from adapters.version_detect import detect_sw_version, is_sw_running


def test_start_and_version(adapter):
    """测试启动 SW 并检测版本"""
    print('\n=== 测试: 启动 SW ===')
    
    success = adapter.start(visible=True, user_control=True)
    
    if success:
        version = adapter.get_revision()
        print(f'  ✓ 启动成功，版本: {version}')
        return True
    else:
        print('  ✗ 启动失败')
        return False


def test_new_part(adapter):
    """测试新建零件"""
    print('\n=== 测试: 新建零件 ===')
    
    try:
        part = adapter.new_part()
        
        if part:
            doc_type = adapter.get_current_doc_type()
            print(f'  ✓ 新建零件成功，文档类型: {doc_type}')
            return True
        else:
            print('  ✗ 新建零件失败')
            return False
    except Exception as e:
        print(f'  ✗ 新建零件异常: {e}')
        return False


def test_sketch_operations(adapter):
    """测试草图操作（基础绘图）"""
    print('\n=== 测试: 草图操作 ===')
    
    results = []
    
    try:
        success = adapter.enter_sketch("前视基准面")
        results.append(('进入草图', success))
        print(f'  {"✓" if success else "✗"} 进入草图')
        time.sleep(0.5)

        success = adapter.draw_line(0, 0, 0, 0.050, 0, 0)
        results.append(('画直线', success))
        print(f'  {"✓" if success else "✗"} 画直线')

        success = adapter.draw_center_line(0, 0, 0, 0.100, 0, 0)
        results.append(('画中心线', success))
        print(f'  {"✓" if success else "✗"} 画中心线')

        success = adapter.draw_circle(0.050, 0.015, 0, 0.050, 0.020, 0)
        results.append(('画圆', success))
        print(f'  {"✓" if success else "✗"} 画圆')

        success = adapter.draw_rect(0.020, 0.030, 0, 0.040, 0.045, 0)
        results.append(('画矩形', success))
        print(f'  {"✓" if success else "✗"} 画矩形')

        success = adapter.draw_arc(0.030, 0, 0, 0.030, 0.010, 0, 0.040, 0.010, 0, 1)
        results.append(('画圆弧', success))
        print(f'  {"✓" if success else "✗"} 画圆弧')

        success = adapter.add_to_db()
        results.append(('提交草图', success))
        print(f'  {"✓" if success else "✗"} 提交草图')

        success = adapter.exit_sketch()
        results.append(('退出草图', success))
        print(f'  {"✓" if success else "✗"} 退出草图')

        return all(r[1] for r in results)
    
    except Exception as e:
        print(f'  ✗ 草图操作异常: {e}')
        return False


def test_feature_extrude(adapter):
    """测试拉伸凸台（使用独立封闭草图）"""
    print('\n=== 测试: 拉伸凸台 ===')
    
    try:
        adapter.enter_sketch("前视基准面")
        adapter.draw_rect(0.010, 0.010, 0, 0.030, 0.025, 0)
        adapter.add_to_db()
        adapter.exit_sketch()
        time.sleep(0.5)

        adapter.clear_selection()
        adapter.select_sketch("草图2")
        
        feat = adapter.extrude(0.020, direction_type=0)
        
        if feat:
            print('  ✓ 拉伸凸台成功')
            return True
        else:
            print('  ✗ 拉伸凸台失败')
            return False
    except Exception as e:
        print(f'  ✗ 拉伸凸台异常: {e}')
        return False


def test_feature_revolve(adapter):
    """测试旋转凸台"""
    print('\n=== 测试: 旋转凸台 ===')
    
    try:
        adapter.enter_sketch("前视基准面")
        adapter.draw_center_line(0, 0, 0, 0.080, 0, 0)
        adapter.draw_line(0, 0, 0, 0, 0.015, 0)
        adapter.draw_line(0, 0.015, 0, 0.080, 0.015, 0)
        adapter.draw_line(0.080, 0.015, 0, 0.080, 0, 0)
        adapter.add_to_db()
        adapter.exit_sketch()
        time.sleep(0.5)

        adapter.clear_selection()
        adapter.select_sketch("草图3")
        
        feat = adapter.revolve(2 * math.pi, revolve_type=0)
        
        if feat:
            print('  ✓ 旋转凸台成功')
            return True
        else:
            print('  ✗ 旋转凸台失败')
            return False
    except Exception as e:
        print(f'  ✗ 旋转凸台异常: {e}')
        return False


def test_feature_cut_extrude(adapter):
    """测试拉伸切除"""
    print('\n=== 测试: 拉伸切除 ===')
    
    try:
        adapter.enter_sketch("前视基准面")
        adapter.draw_circle(0.040, 0, 0, 0.040, 0.005, 0)
        adapter.add_to_db()
        adapter.exit_sketch()
        time.sleep(0.5)

        adapter.clear_selection()
        adapter.select_sketch("草图4")
        
        feat = adapter.cut_extrude(0.020, through_all=True)
        
        if feat:
            print('  ✓ 拉伸切除成功')
            return True
        else:
            print('  ✗ 拉伸切除失败')
            return False
    except Exception as e:
        print(f'  ✗ 拉伸切除异常: {e}')
        return False


def test_feature_revolve_cut(adapter):
    """测试旋转切除（使用封闭草图，确保与实体相交）"""
    print('\n=== 测试: 旋转切除 ===')
    
    try:
        adapter.enter_sketch("前视基准面")
        adapter.draw_center_line(0, 0, 0, 0.080, 0, 0)
        adapter.draw_line(0.020, 0, 0, 0.020, 0.015, 0)
        adapter.draw_line(0.020, 0.015, 0, 0.025, 0.015, 0)
        adapter.draw_line(0.025, 0.015, 0, 0.025, 0, 0)
        adapter.draw_line(0.025, 0, 0, 0.020, 0, 0)
        adapter.add_to_db()
        adapter.exit_sketch()
        time.sleep(0.5)

        adapter.clear_selection()
        adapter.select_sketch("草图5")
        
        feat = adapter.revolve_cut(2 * math.pi)
        
        if feat:
            print('  ✓ 旋转切除成功')
            return True
        else:
            print('  ✗ 旋转切除失败')
            return False
    except Exception as e:
        print(f'  ✗ 旋转切除异常: {e}')
        return False


def test_feature_tree(adapter):
    """测试特征树遍历"""
    print('\n=== 测试: 特征树遍历 ===')
    
    try:
        features = adapter.get_features()
        
        if features:
            print(f'  ✓ 遍历特征树成功，共 {len(features)} 个特征')
            for f in features:
                print(f'    - {f["name"]} [{f["type_name"]}]')
            return True
        else:
            print('  ✗ 特征树为空')
            return False
    except Exception as e:
        print(f'  ✗ 特征树遍历异常: {e}')
        return False


def test_save_and_quit(adapter):
    """测试保存和退出"""
    print('\n=== 测试: 保存和退出 ===')
    
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '.trae', 'tests', 'output')
        os.makedirs(output_dir, exist_ok=True)
        temp_path = os.path.join(output_dir, 'test_solidworks_adapter.sldprt')
        
        save_success = adapter.save_doc(temp_path)
        if save_success:
            print(f'  ✓ 保存成功: {temp_path}')
        else:
            print('  ✗ 保存失败')
        
        quit_success = adapter.quit()
        print(f'  {"✓" if quit_success else "✗"} 退出 SW')
        
        return save_success and quit_success
    except Exception as e:
        print(f'  ✗ 保存退出异常: {e}')
        return False


def run_all_tests():
    """运行所有单步指令测试"""
    print('=' * 60)
    print('SolidWorksAdapter 单步指令验收测试')
    print('=' * 60)
    print(f'SW 版本检测: {detect_sw_version()}')
    print(f'SW 是否运行: {is_sw_running()}')

    adapter = SolidWorksAdapter()
    
    tests = [
        ('启动 SW', test_start_and_version),
        ('新建零件', test_new_part),
        ('草图操作', test_sketch_operations),
        ('拉伸凸台', test_feature_extrude),
        ('旋转凸台', test_feature_revolve),
        ('拉伸切除', test_feature_cut_extrude),
        ('旋转切除', test_feature_revolve_cut),
        ('特征树遍历', test_feature_tree),
        ('保存退出', test_save_and_quit),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func(adapter)
            results.append((name, result))
        except Exception as e:
            print(f'\n=== 测试: {name} ===')
            print(f'  ✗ 测试异常: {e}')
            results.append((name, False))

    print('\n' + '=' * 60)
    print('测试结果汇总')
    print('=' * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = '✓ 通过' if result else '✗ 失败'
        print(f'  {name}: {status}')
    
    print(f'\n  总计: {passed}/{total} 通过')
    
    if passed == total:
        print('  状态: 全部通过')
    else:
        print('  状态: 存在失败项，需修复')
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)