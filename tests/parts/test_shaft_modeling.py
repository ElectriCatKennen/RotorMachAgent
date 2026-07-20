#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOLIDWORKS API 三维建模测试：阶梯轴

通过 Python + pywin32 + comtypes 调用 SOLIDWORKS COM API，自动创建一根包含以下特征的阶梯轴：
- 7段阶梯轴主体（旋转特征）
- 2个轴承位（Ø35）
- 2个弹性挡圈槽（旋转切除）
- 1个圆螺母螺纹段（M30装饰螺纹线，待实现）
- 2个键槽（拉伸切除）

轴设计（从左到右）：
    段1: Ø30 × 50  左端键槽段
    段2: Ø40 × 3   轴肩
    段3: Ø35 × 25  左轴承位（含挡圈槽）
    段4: Ø50 × 60  中间段
    段5: Ø35 × 25  右轴承位（含挡圈槽）
    段6: Ø26 × 4   退刀槽
    段7: Ø30 × 25  右端螺纹段（M30）
    总长: 192mm
"""
import win32com.client
import pythoncom
import time
import math
import os
import subprocess
import struct
import comtypes
import comtypes.client
from ctypes import cast as ct_cast, c_void_p, POINTER

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SW_TLB = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\sldworks.tlb"

CALLOUT_NONE = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
MISSING = win32com.client.VARIANT(pythoncom.VT_ERROR, 0x80020004)

print('[0] 加载 sldworks.tlb 类型库...')
try:
    sw_mod = comtypes.client.GetModule(SW_TLB)
    import comtypes.gen.SldWorks as sw_gen
    print(f'  [OK] 类型库已加载')
except Exception as e:
    print(f'  [WARN] 类型库加载失败: {e}')
    sw_gen = None


def bridge_to_comtypes(pywin32_obj, target_interface):
    """将 pywin32 的 PyIDispatch 对象桥接到 comtypes 的类型化接口

    通过提取 pywin32 PyIDispatch 内部的 COM 指针（内存 offset 16），
    用 comtypes 包装为 IUnknown，再 QueryInterface 到目标接口。
    """
    ole_obj = pywin32_obj._oleobj_
    obj_id = id(ole_obj)
    mem = (comtypes.c_byte * 64).from_address(obj_id)
    com_ptr = struct.unpack_from('<Q', mem, 16)[0]
    iunknown_ptr = ct_cast(c_void_p(com_ptr), POINTER(comtypes.IUnknown))
    iunknown_ptr.AddRef()
    return iunknown_ptr.QueryInterface(target_interface)


def m(mm):
    """毫米转米（SW API 坐标单位为米）"""
    return mm / 1000.0


def select_sketch(part, sketch_name):
    """多种方式尝试选择草图，提高鲁棒性"""
    part.ClearSelection2(True)

    sketch_num = sketch_name[-1] if sketch_name[-1].isdigit() else ""
    for name in [f"草图{sketch_num}", sketch_name, "草图1", "草图2",
                 "草图3", "草图4", "草图5"]:
        try:
            if part.Extension.SelectByID2(name, "SKETCH", 0, 0, 0, False, 0,
                                           CALLOUT_NONE, 0):
                print(f'  选择草图: {name}')
                return True
        except Exception:
            pass

    try:
        feat = part.FirstFeature
        latest_sketch = None
        while feat:
            try:
                if feat.GetTypeName == "ProfileFeature":
                    if "<" not in feat.Name:
                        latest_sketch = feat
            except Exception:
                pass
            try:
                feat = feat.GetNextFeature
            except Exception:
                break
        if latest_sketch:
            print(f'  遍历找到草图: {latest_sketch.Name}')
            latest_sketch.Select2(False, 0)
            return True
    except Exception as e:
        print(f'  [WARN] 遍历特征失败: {e}')

    return False


def create_shaft():
    """创建阶梯轴零件"""
    print('[1] 启动 SOLIDWORKS...')
    subprocess.run(['taskkill', '/f', '/im', 'sldworks.exe'], capture_output=True)
    time.sleep(2)

    sw_app = win32com.client.Dispatch('SldWorks.Application')
    sw_app.Visible = True
    sw_app.UserControl = True
    print(f'  [OK] Revision: {sw_app.RevisionNumber}')
    time.sleep(2)

    part = None
    try:
        print('[2] 新建零件...')
        import glob
        templates = glob.glob(r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\gb_part.prtdot")
        if not templates:
            templates = glob.glob(r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\*part*.prtdot")
        if templates:
            template = templates[0]
            print(f'  模板: {template}')
            part = sw_app.NewDocument(template, 0, 0, 0)
        else:
            print('  [FAIL] 未找到零件模板')
            return
        if not part:
            print('  [FAIL] NewDocument 返回 None')
            return
        print(f'  [OK] 零件已创建')
        time.sleep(1)

        # ===== 3. 旋转创建轴主体 =====
        print('[3] 创建旋转草图（轴剖面）...')
        part.Extension.SelectByID2("前视基准面", "PLANE", 0, 0, 0, False, 0, CALLOUT_NONE, 0)
        part.SketchManager.InsertSketch(True)
        time.sleep(0.5)

        # 画中心线（旋转轴，沿X轴）
        part.SketchManager.CreateCenterLine(0, 0, 0, m(192), 0, 0)

        # 旋转剖面点（单位：米，X轴向右，Y为半径）
        points = [
            (0, 0),              # 中心线起点
            (0, m(15)),          # 左端面 Ø30
            (m(50), m(15)),      # 段1结束
            (m(50), m(20)),      # 轴肩 Ø40
            (m(53), m(20)),      # 段2结束
            (m(53), m(17.5)),    # 降到 Ø35（左轴承位）
            (m(78), m(17.5)),    # 段3结束
            (m(78), m(25)),      # 轴肩 Ø50
            (m(138), m(25)),     # 段4结束
            (m(138), m(17.5)),   # 降到 Ø35（右轴承位）
            (m(163), m(17.5)),   # 段5结束
            (m(163), m(13)),     # 退刀槽 Ø26
            (m(167), m(13)),     # 退刀槽结束
            (m(167), m(15)),     # 螺纹段 Ø30
            (m(192), m(15)),     # 右端面
            (m(192), 0),         # 回到中心线
        ]

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            part.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)

        part.SketchManager.AddToDB = True
        time.sleep(0.5)

        # ===== 4. 创建旋转特征 =====
        # 实际签名（comtypes 类型库验证）：
        # FeatureRevolve(Angle, ReverseDir, Angle2, RevType, Options,
        #                Merge, UseFeatScope, UseAutoSel)
        # 注意：Angle/Angle2 单位为弧度！
        # RevType: 0=单向, 1=双向, 2=中面
        print('[4] 创建旋转特征（360°）...')
        shaft_feat = None

        try:
            shaft_feat = part.FeatureManager.FeatureRevolve(
                2 * math.pi,  # Angle: 360°（弧度）
                False,        # ReverseDir: 不反向
                0,            # Angle2: 第二方向角度（单向时为0）
                0,            # RevType: 0=单向
                0,            # Options: 0=默认
                True,         # Merge: 合并到实体
                True,         # UseFeatScope
                True          # UseAutoSel
            )
        except Exception as e1:
            print(f'  [WARN] FeatureRevolve: {e1}')

        # 备用：退出草图后重试
        if not shaft_feat:
            print('  [INFO] 尝试退出草图后重试...')
            part.SketchManager.InsertSketch(True)
            time.sleep(0.5)
            part.Extension.SelectByID2("草图1", "SKETCH", 0, 0, 0, False, 0, CALLOUT_NONE, 0)
            try:
                shaft_feat = part.FeatureManager.FeatureRevolve(
                    2 * math.pi, False, 0, 0, 0, True, True, True
                )
            except Exception as e4:
                print(f'  [FAIL] 重试失败: {e4}')

        if shaft_feat:
            print(f'  [OK] 轴主体创建成功: {shaft_feat.Name}')
        else:
            print('  [FAIL] 轴主体创建失败，终止')
            return

        time.sleep(1)

        # ===== 5. 左端键槽 =====
        print('[5] 创建左端键槽...')
        try:
            create_keyslot(part, x_start_mm=15, length_mm=25, width_mm=8,
                          depth_mm=4, radius_mm=15, sketch_name="草图2")
        except Exception as e:
            print(f'  [WARN] 左端键槽: {e}')
            import traceback
            traceback.print_exc()

        # ===== 6. 右端键槽 =====
        print('[6] 创建右端键槽...')
        try:
            create_keyslot(part, x_start_mm=172, length_mm=20, width_mm=8,
                          depth_mm=4, radius_mm=15, sketch_name="草图3")
        except Exception as e:
            print(f'  [WARN] 右端键槽: {e}')
            import traceback
            traceback.print_exc()

        # ===== 7. 左挡圈槽 =====
        print('[7] 创建左挡圈槽...')
        try:
            create_circlip_groove(part, x_center_mm=57.5, width_mm=3,
                                 depth_mm=1.5, outer_radius_mm=17.5,
                                 sketch_name="草图4")
        except Exception as e:
            print(f'  [WARN] 左挡圈槽: {e}')
            import traceback
            traceback.print_exc()

        # ===== 8. 右挡圈槽 =====
        print('[8] 创建右挡圈槽...')
        try:
            create_circlip_groove(part, x_center_mm=157.5, width_mm=3,
                                 depth_mm=1.5, outer_radius_mm=17.5,
                                 sketch_name="草图5")
        except Exception as e:
            print(f'  [WARN] 右挡圈槽: {e}')
            import traceback
            traceback.print_exc()

        # ===== 9. 装饰螺纹线（M30，尝试性功能） =====
        print('[9] 创建装饰螺纹线（M30）...')
        try:
            create_decorative_thread(part, sw_app, x_start_mm=167,
                                    length_mm=25, diameter_mm=30)
        except Exception as e:
            print(f'  [WARN] 装饰螺纹线: {e}')
            import traceback
            traceback.print_exc()

        # ===== 10. 保存 =====
        print('[10] 保存零件...')
        save_path = os.path.join(OUTPUT_DIR, '阶梯轴.SLDPRT')
        if os.path.exists(save_path):
            os.remove(save_path)
        errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        try:
            result = part.SaveAs4(save_path, 0, 0, errors, warnings)
            print(f'  [OK] 已保存(SaveAs4): {save_path}')
        except Exception:
            try:
                result = part.SaveAs3(save_path, 0, 0)
                print(f'  [OK] 已保存(SaveAs3): {save_path}')
            except Exception as e:
                print(f'  [WARN] 保存失败: {e}')

        print('\n>>> 阶梯轴建模完成! <<<')

    except Exception as e:
        print(f'\n[FAIL] Error: {e}')
        import traceback
        traceback.print_exc()


def create_keyslot(part, x_start_mm, length_mm, width_mm, depth_mm, radius_mm, sketch_name):
    """创建键槽（在前视基准面画矩形，两侧对称切除拉伸）"""
    part.ClearSelection2(True)
    selected_plane = False
    for plane_name in ["前视基准面", "Front"]:
        if part.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, CALLOUT_NONE, 0):
            selected_plane = True
            break
    if not selected_plane:
        print(f'  [WARN] 无法选择前视基准面')
        return

    part.SketchManager.InsertSketch(True)
    time.sleep(0.5)

    x1 = m(x_start_mm)
    x2 = m(x_start_mm + length_mm)
    y1 = m(radius_mm - depth_mm)
    y2 = m(radius_mm)

    part.SketchManager.CreateLine(x1, y1, 0, x2, y1, 0)
    part.SketchManager.CreateLine(x2, y1, 0, x2, y2, 0)
    part.SketchManager.CreateLine(x2, y2, 0, x1, y2, 0)
    part.SketchManager.CreateLine(x1, y2, 0, x1, y1, 0)

    part.SketchManager.AddToDB = True
    time.sleep(0.5)

    part.SketchManager.InsertSketch(True)
    time.sleep(0.5)

    if not select_sketch(part, sketch_name):
        print(f'  [WARN] 无法选择草图')
        return

    half_width = m(width_mm / 2)
    cut_feat = None

    if sw_gen:
        try:
            fm_typed = bridge_to_comtypes(part.FeatureManager, sw_gen.IFeatureManager)
            cut_feat = fm_typed.FeatureCut3(
                False,  # Sd: 非单方向（要两侧）
                False,  # Flip
                True,   # Dir: 两侧对称
                0, 0,   # T1, T2: 盲端
                half_width, half_width,  # D1, D2
                False, False, False, False,  # 拔模
                0, 0,   # 拔模角度
                False, False, False, False,  # Offset, Translate
                False,  # NormalCut
                True, True,  # UseFeatScope, UseAutoSelect
                False, False, False,  # Assembly
                0, 0, False  # T0, StartOffset, FlipStartOffset
            )
            if cut_feat:
                print(f'  [OK] 键槽创建成功(FeatureCut3): {cut_feat.Name}')
                return
            print(f'  [WARN] FeatureCut3 返回 None')
        except Exception as e:
            print(f'  [WARN] FeatureCut3: {e}')

    # 降级：pywin32 FeatureCut
    if not cut_feat:
        try:
            cut_feat = part.FeatureManager.FeatureCut(
                False, False, True, 0, 0,
                half_width, half_width,
                False, False, False, False,
                0, 0,
                False, False, False, False,
                False, True, True
            )
            if cut_feat:
                print(f'  [OK] 键槽创建成功(FeatureCut): {cut_feat.Name}')
        except Exception as e:
            print(f'  [WARN] FeatureCut: {e}')


def create_circlip_groove(part, x_center_mm, width_mm, depth_mm, outer_radius_mm, sketch_name):
    """创建挡圈槽（旋转切除）"""
    part.ClearSelection2(True)
    selected_plane = False
    for plane_name in ["前视基准面", "Front"]:
        if part.Extension.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 0, CALLOUT_NONE, 0):
            selected_plane = True
            break
    if not selected_plane:
        print(f'  [WARN] 无法选择前视基准面')
        return

    part.SketchManager.InsertSketch(True)
    time.sleep(0.5)

    # 画挡圈槽矩形剖面
    x1 = m(x_center_mm - width_mm / 2)
    x2 = m(x_center_mm + width_mm / 2)
    y1 = m(outer_radius_mm - depth_mm)
    y2 = m(outer_radius_mm)

    part.SketchManager.CreateLine(x1, y1, 0, x2, y1, 0)
    part.SketchManager.CreateLine(x2, y1, 0, x2, y2, 0)
    part.SketchManager.CreateLine(x2, y2, 0, x1, y2, 0)
    part.SketchManager.CreateLine(x1, y2, 0, x1, y1, 0)

    # 画中心线（旋转轴）
    part.SketchManager.CreateCenterLine(0, 0, 0, m(192), 0, 0)

    part.SketchManager.AddToDB = True
    time.sleep(0.5)

    part.SketchManager.InsertSketch(True)
    time.sleep(0.5)

    if not select_sketch(part, sketch_name):
        print(f'  [WARN] 无法选择草图')
        return

    # comtypes vtable 调用 FeatureRevolveCut2
    if sw_gen:
        try:
            fm_typed = bridge_to_comtypes(part.FeatureManager, sw_gen.IFeatureManager)
            cut_feat = fm_typed.FeatureRevolveCut2(
                2 * math.pi,  # Angle
                False,        # ReverseDir
                0,            # Angle2
                0,            # RevType
                0,            # Options
                True,         # UseFeatScope
                True,         # UseAutoSelect
                False,        # AssemblyFeatureScope
                False,        # AutoSelectComponents
                False         # PropagateFeatureToParts
            )
            if cut_feat:
                print(f'  [OK] 挡圈槽创建成功: {cut_feat.Name}')
            else:
                print(f'  [WARN] FeatureRevolveCut2 返回 None')
        except Exception as e:
            print(f'  [WARN] FeatureRevolveCut2: {e}')


def create_decorative_thread(part, sw_app, x_start_mm, length_mm, diameter_mm):
    """创建装饰螺纹线（M30）

    选择螺纹段的圆柱面，插入装饰螺纹线。

    注意：InsertCosmeticThread 在部分 SW 版本下不可用，
    此函数为尝试性实现，失败不影响几何模型。
    """
    x_mid = m(x_start_mm + length_mm / 2)
    z = m(diameter_mm / 2)

    part.ClearSelection2(True)
    result = part.Extension.SelectByID2("", "FACE", x_mid, 0, z, False, 0, CALLOUT_NONE, 0)
    time.sleep(0.3)

    if not result:
        part.Extension.SelectByID2("", "FACE", x_mid, z, 0, False, 0, CALLOUT_NONE, 0)
        time.sleep(0.3)

    thread_feat = None
    try:
        thread_feat = part.Extension.InsertCosmeticThread(
            m(diameter_mm),       # major diameter (大径)
            m(diameter_mm - 1.5), # minor diameter (小径，M30粗牙螺距3.5，小径约26.5)
            3.5,                  # pitch (mm，M30粗牙螺距3.5mm)
            m(length_mm),         # length
            0                     # type
        )
    except Exception as e1:
        print(f'  [WARN] Extension.InsertCosmeticThread: {e1}')
        try:
            thread_feat = part.FeatureManager.InsertCosmeticThread(
                m(diameter_mm),
                m(diameter_mm - 1.5),
                3.5,
                m(length_mm),
                0
            )
        except Exception as e2:
            print(f'  [WARN] FeatureManager.InsertCosmeticThread: {e2}')

    if thread_feat:
        print(f'  [OK] 装饰螺纹线创建成功: {thread_feat.Name}')
    else:
        print(f'  [WARN] 装饰螺纹线未创建（不影响几何模型）')


if __name__ == '__main__':
    create_shaft()
