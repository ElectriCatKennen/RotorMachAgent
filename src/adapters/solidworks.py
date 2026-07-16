"""SolidWorks 适配器 - 封装 SW COM API 为原子工具

基于已验证的 SW API 单步指令参考（docs/01_SW_API单步指令参考.md）
"""

import win32com.client
import pythoncom
import subprocess
import time
import glob
from typing import Optional, Any

from .comtypes_bridge import get_feature_manager_vtable

CALLOUT_NONE = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)

SW_DOC_PART = 1
SW_DOC_ASSEMBLY = 2
SW_DOC_DRAWING = 3

SW_FEATURE_BLIND = 0
SW_FEATURE_THROUGH_ALL = 1
SW_FEATURE_TO_NEXT = 2
SW_FEATURE_TO_SURFACE = 3
SW_FEATURE_BOTH_SIDES_TO_SURFACE = 4

SW_REVOLVE_TYPE_ONE_DIRECTION = 0
SW_REVOLVE_TYPE_TWO_DIRECTIONS = 1
SW_REVOLVE_TYPE_MID_PLANE = 2


class SolidWorksAdapter:
    def __init__(self, sw_version: str = "2023"):
        self.sw_app = None
        self.current_doc = None
        self.sw_version = sw_version
        self._initialized = False

    def start(self, visible: bool = True, user_control: bool = True) -> bool:
        """启动 SOLIDWORKS

        Args:
            visible: 是否显示窗口（建议 True，便于调试）
            user_control: 是否允许用户交互

        Returns:
            True 成功，False 失败
        """
        try:
            subprocess.run(['taskkill', '/f', '/im', 'sldworks.exe'], capture_output=True)
            time.sleep(2)

            self.sw_app = win32com.client.Dispatch('SldWorks.Application')
            self.sw_app.Visible = visible
            self.sw_app.UserControl = user_control
            time.sleep(2)

            revision = self.sw_app.RevisionNumber
            print(f'SOLIDWORKS 启动成功，版本: {revision}')
            self._initialized = True
            return True
        except Exception as e:
            print(f'SOLIDWORKS 启动失败: {e}')
            return False

    def quit(self) -> bool:
        """退出 SOLIDWORKS

        Returns:
            True 成功，False 失败
        """
        try:
            if self.sw_app:
                self.sw_app.ExitApp()
                time.sleep(1)
            subprocess.run(['taskkill', '/f', '/im', 'sldworks.exe'], capture_output=True)
            self._initialized = False
            return True
        except Exception as e:
            print(f'退出失败: {e}')
            return False

    def new_part(self, template_path: str = None) -> Optional[Any]:
        """新建零件文档

        Args:
            template_path: 模板路径，为空时自动查找国标模板

        Returns:
            ModelDoc2 对象，失败返回 None
        """
        if not self._initialized:
            print('SW 未启动')
            return None

        try:
            if template_path is None:
                templates = glob.glob(
                    r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\gb_part.prtdot"
                )
                if not templates:
                    templates = glob.glob(
                        r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\*part*.prtdot"
                    )
                if templates:
                    template_path = templates[0]
                else:
                    print('未找到零件模板')
                    return None

            self.current_doc = self.sw_app.NewDocument(template_path, 0, 0, 0)
            return self.current_doc
        except Exception as e:
            print(f'新建零件失败: {e}')
            return None

    def new_assembly(self, template_path: str = None) -> Optional[Any]:
        """新建装配体文档

        Args:
            template_path: 模板路径，为空时自动查找

        Returns:
            ModelDoc2 对象，失败返回 None
        """
        if not self._initialized:
            print('SW 未启动')
            return None

        try:
            if template_path is None:
                templates = glob.glob(
                    r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\gb_assembly.asmdot"
                )
                if not templates:
                    templates = glob.glob(
                        r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\*assembly*.asmdot"
                    )
                if templates:
                    template_path = templates[0]
                else:
                    print('未找到装配体模板')
                    return None

            self.current_doc = self.sw_app.NewDocument(template_path, 0, 0, 0)
            return self.current_doc
        except Exception as e:
            print(f'新建装配体失败: {e}')
            return None

    def new_drawing(self, template_path: str = None) -> Optional[Any]:
        """新建工程图文档

        Args:
            template_path: 模板路径，为空时自动查找

        Returns:
            ModelDoc2 对象，失败返回 None
        """
        if not self._initialized:
            print('SW 未启动')
            return None

        try:
            if template_path is None:
                templates = glob.glob(
                    r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\gb_drawing.drwdot"
                )
                if not templates:
                    templates = glob.glob(
                        r"C:\ProgramData\SolidWorks\SOLIDWORKS *\templates\*drawing*.drwdot"
                    )
                if templates:
                    template_path = templates[0]
                else:
                    print('未找到工程图模板')
                    return None

            self.current_doc = self.sw_app.NewDocument(template_path, 0, 0, 0)
            return self.current_doc
        except Exception as e:
            print(f'新建工程图失败: {e}')
            return None

    def open_doc(self, filepath: str, doc_type: int = SW_DOC_PART) -> Optional[Any]:
        """打开已有文档

        Args:
            filepath: 文件路径
            doc_type: 文档类型（1=零件, 2=装配体, 3=工程图）

        Returns:
            ModelDoc2 对象，失败返回 None
        """
        if not self._initialized:
            print('SW 未启动')
            return None

        try:
            errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

            self.current_doc = self.sw_app.OpenDoc6(
                filepath,
                doc_type,
                1,
                "",
                errors,
                warnings
            )
            return self.current_doc
        except Exception as e:
            print(f'打开文件失败: {e}')
            return None

    def save_doc(self, filepath: str) -> bool:
        """保存文档

        Args:
            filepath: 保存路径

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            import os
            dir_path = os.path.dirname(filepath)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)

            errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

            result = self.current_doc.SaveAs4(
                filepath,
                0,
                0,
                errors,
                warnings
            )
            return result == 0 or os.path.exists(filepath)
        except Exception as e:
            print(f'保存失败: {e}')
            return False

    def select_by_id(self, name: str, obj_type: str, append: bool = False) -> bool:
        """选择对象（SelectByID2）

        Args:
            name: 对象名称（中文版用中文，如"前视基准面"）
            obj_type: 对象类型（"PLANE", "SKETCH", "FACE", "EDGE", "VERTEX", ""）
            append: 是否追加到选择集

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            result = self.current_doc.Extension.SelectByID2(
                name,
                obj_type,
                0, 0, 0,
                append,
                0,
                CALLOUT_NONE,
                0
            )
            return result
        except Exception as e:
            print(f'选择失败: {e}')
            return False

    def select_plane(self, plane_name: str = "前视基准面", append: bool = False) -> bool:
        """选择基准面

        Args:
            plane_name: 基准面名称，优先尝试中文名
            append: 是否追加

        Returns:
            True 成功，False 失败
        """
        success = self.select_by_id(plane_name, "PLANE", append)
        if not success and plane_name != "前视基准面":
            success = self.select_by_id("前视基准面", "PLANE", append)
        return success

    def select_sketch(self, sketch_name: str = "草图1", append: bool = False) -> bool:
        """选择草图

        Args:
            sketch_name: 草图名称
            append: 是否追加

        Returns:
            True 成功，False 失败
        """
        return self.select_by_id(sketch_name, "SKETCH", append)

    def clear_selection(self) -> bool:
        """清空选择集

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            return False
        try:
            self.current_doc.ClearSelection2(True)
            return True
        except Exception as e:
            print(f'清空选择失败: {e}')
            return False

    def enter_sketch(self, plane_name: str = "前视基准面") -> bool:
        """进入草图编辑模式

        Args:
            plane_name: 基准面名称

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.clear_selection()
            self.select_plane(plane_name)
            self.current_doc.SketchManager.InsertSketch(True)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f'进入草图失败: {e}')
            return False

    def exit_sketch(self) -> bool:
        """退出草图编辑模式

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.AddToDB = True
            time.sleep(0.5)
            self.current_doc.SketchManager.InsertSketch(True)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f'退出草图失败: {e}')
            return False

    def draw_line(self, x1: float, y1: float, z1: float,
                 x2: float, y2: float, z2: float) -> bool:
        """画直线

        Args:
            x1, y1, z1: 起点坐标（米）
            x2, y2, z2: 终点坐标（米）

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.CreateLine(x1, y1, z1, x2, y2, z2)
            return True
        except Exception as e:
            print(f'画线失败: {e}')
            return False

    def draw_center_line(self, x1: float, y1: float, z1: float,
                        x2: float, y2: float, z2: float) -> bool:
        """画中心线（旋转轴）

        Args:
            x1, y1, z1: 起点坐标（米）
            x2, y2, z2: 终点坐标（米）

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.CreateCenterLine(x1, y1, z1, x2, y2, z2)
            return True
        except Exception as e:
            print(f'画中心线失败: {e}')
            return False

    def draw_circle(self, xc: float, yc: float, zc: float,
                    xp: float, yp: float, zp: float) -> bool:
        """画圆

        Args:
            xc, yc, zc: 圆心坐标（米）
            xp, yp, zp: 圆上一点（米）

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.CreateCircle(xc, yc, zc, xp, yp, zp)
            return True
        except Exception as e:
            print(f'画圆失败: {e}')
            return False

    def draw_rect(self, x1: float, y1: float, z1: float,
                  x2: float, y2: float, z2: float) -> bool:
        """画矩形

        Args:
            x1, y1, z1: 对角点1（米）
            x2, y2, z2: 对角点2（米）

        Returns:
            True 成功，False 失败

        Note:
            CreateCornerRect 在 IDispatch 中不可用，用四条直线绘制矩形
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.CreateLine(x1, y1, z1, x2, y1, z1)
            self.current_doc.SketchManager.CreateLine(x2, y1, z1, x2, y2, z1)
            self.current_doc.SketchManager.CreateLine(x2, y2, z1, x1, y2, z1)
            self.current_doc.SketchManager.CreateLine(x1, y2, z1, x1, y1, z1)
            return True
        except Exception as e:
            print(f'画矩形失败: {e}')
            return False

    def draw_arc(self, xc: float, yc: float, zc: float,
                 xp1: float, yp1: float, zp1: float,
                 xp2: float, yp2: float, zp2: float,
                 direction: int = 1) -> bool:
        """画圆弧

        Args:
            xc, yc, zc: 圆心坐标（米）
            xp1, yp1, zp1: 起点（米）
            xp2, yp2, zp2: 终点（米）
            direction: 1=逆时针, -1=顺时针

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.CreateArc(
                xc, yc, zc, xp1, yp1, zp1, xp2, yp2, zp2, direction
            )
            return True
        except Exception as e:
            print(f'画圆弧失败: {e}')
            return False

    def add_to_db(self) -> bool:
        """提交草图到数据库

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            print('没有活动文档')
            return False

        try:
            self.current_doc.SketchManager.AddToDB = True
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f'提交草图失败: {e}')
            return False

    def extrude(self, depth: float, direction_type: int = SW_FEATURE_BLIND,
                flip: bool = False, merge: bool = True) -> Optional[Any]:
        """拉伸凸台

        Args:
            depth: 拉伸深度（米）
            direction_type: 拉伸类型（0=盲端, 1=完全贯穿, 2=到下一面）
            flip: 是否反向
            merge: 是否合并

        Returns:
            特征对象，失败返回 None
        """
        if not self.current_doc:
            print('没有活动文档')
            return None

        try:
            feat = self.current_doc.FeatureManager.FeatureExtrusion2(
                True,   # Sd: 单方向
                flip,   # Flip
                False,  # Dir: 两侧对称
                direction_type,  # T1
                0,              # T2
                depth,          # D1
                0,              # D2
                False, False, False, False,  # 拔模
                0, 0,                        # 拔模角度
                False, False, False, False,  # Offset, Translate
                merge,          # Merge
                True,           # UseFeatScope
                True,           # UseAutoSelect
                0, 0, False     # T0, StartOffset, FlipStartOffset
            )
            return feat
        except Exception as e:
            print(f'拉伸失败: {e}')
            return None

    def cut_extrude(self, depth: float, direction_type: int = SW_FEATURE_BLIND,
                    flip: bool = False, through_all: bool = False) -> Optional[Any]:
        """拉伸切除

        Args:
            depth: 切除深度（米）
            direction_type: 切除类型
            flip: 是否反向
            through_all: 是否完全贯穿

        Returns:
            特征对象，失败返回 None
        """
        if not self.current_doc:
            print('没有活动文档')
            return None

        try:
            if through_all:
                direction_type = SW_FEATURE_THROUGH_ALL
                depth = 0

            fm = get_feature_manager_vtable(self.current_doc)
            if fm is None:
                print('comtypes 桥接失败，尝试 pywin32')
                fm_pywin32 = self.current_doc.FeatureManager
                feat = fm_pywin32.FeatureCut3(
                    True, False, False,
                    direction_type, 0,
                    depth, 0,
                    False, False, False, False,
                    0, 0,
                    False, False, False, False,
                    False, True, True,
                    False, False, False,
                    0, 0, False
                )
            else:
                feat = fm.FeatureCut3(
                    True,   # Sd: 单方向
                    flip,   # Flip
                    False,  # Dir
                    direction_type, 0,  # T1, T2
                    depth, 0,           # D1, D2
                    False, False, False, False,  # 拔模
                    0, 0,                        # 拔模角度
                    False, False, False, False,  # Offset, Translate
                    False,           # NormalCut
                    True,            # UseFeatScope
                    True,            # UseAutoSelect
                    False, False, False,  # Assembly
                    0, 0, False           # T0, StartOffset, FlipStartOffset
                )
            return feat
        except Exception as e:
            print(f'拉伸切除失败: {e}')
            return None

    def revolve(self, angle: float, revolve_type: int = SW_REVOLVE_TYPE_ONE_DIRECTION,
                reverse_dir: bool = False, merge: bool = True) -> Optional[Any]:
        """旋转凸台

        Args:
            angle: 旋转角度（弧度）
            revolve_type: 旋转类型（0=单向, 1=双向, 2=中面）
            reverse_dir: 是否反向
            merge: 是否合并

        Returns:
            特征对象，失败返回 None

        Note:
            正确签名（comtypes 类型库验证）：
            FeatureRevolve(Angle, ReverseDir, Angle2, RevType, Options,
                          Merge, UseFeatScope, UseAutoSel)
        """
        if not self.current_doc:
            print('没有活动文档')
            return None

        try:
            feat = self.current_doc.FeatureManager.FeatureRevolve(
                angle,          # Angle: 旋转角度（弧度）
                reverse_dir,    # ReverseDir
                0,              # Angle2
                revolve_type,   # RevType
                0,              # Options
                merge,          # Merge
                True,           # UseFeatScope
                True            # UseAutoSel
            )
            return feat
        except Exception as e:
            print(f'旋转失败: {e}')
            return None

    def revolve_cut(self, angle: float, revolve_type: int = SW_REVOLVE_TYPE_ONE_DIRECTION,
                    reverse_dir: bool = False) -> Optional[Any]:
        """旋转切除

        Args:
            angle: 旋转角度（弧度）
            revolve_type: 旋转类型
            reverse_dir: 是否反向

        Returns:
            特征对象，失败返回 None
        """
        if not self.current_doc:
            print('没有活动文档')
            return None

        try:
            fm = get_feature_manager_vtable(self.current_doc)
            if fm is None:
                print('comtypes 桥接失败，尝试 pywin32')
                fm_pywin32 = self.current_doc.FeatureManager
                feat = fm_pywin32.FeatureRevolveCut2(
                    angle, reverse_dir, 0, revolve_type, 0,
                    True, True, False, False, False
                )
            else:
                feat = fm.FeatureRevolveCut2(
                    angle,          # Angle
                    reverse_dir,    # ReverseDir
                    0,              # Angle2
                    revolve_type,   # RevType
                    0,              # Options
                    True,           # UseFeatScope
                    True,           # UseAutoSelect
                    False, False, False  # Assembly
                )
            return feat
        except Exception as e:
            print(f'旋转切除失败: {e}')
            return None

    def get_features(self) -> list:
        """遍历特征树，获取所有特征信息

        Returns:
            特征信息列表，每个元素包含 name 和 type_name
        """
        if not self.current_doc:
            return []

        features = []
        try:
            feat = self.current_doc.FirstFeature
            while feat:
                features.append({
                    'name': feat.Name,
                    'type_name': feat.GetTypeName
                })
                feat = feat.GetNextFeature
        except Exception as e:
            print(f'遍历特征树失败: {e}')

        return features

    def select_feature(self, feature_name: str) -> bool:
        """通过名称选择特征

        Args:
            feature_name: 特征名称

        Returns:
            True 成功，False 失败
        """
        if not self.current_doc:
            return False

        try:
            feat = self.current_doc.FirstFeature
            while feat:
                if feat.Name == feature_name:
                    feat.Select2(False, 0)
                    return True
                feat = feat.GetNextFeature
            return False
        except Exception as e:
            print(f'选择特征失败: {e}')
            return False

    def get_revision(self) -> str:
        """获取 SW 版本号

        Returns:
            版本号字符串，如 "31.5.0"
        """
        if self.sw_app:
            return self.sw_app.RevisionNumber
        return ""

    def is_initialized(self) -> bool:
        """检查 SW 是否已初始化

        Returns:
            True 已初始化，False 未初始化
        """
        return self._initialized

    def get_current_doc_type(self) -> int:
        """获取当前文档类型

        Returns:
            1=零件, 2=装配体, 3=工程图, 0=无活动文档
        """
        if not self.current_doc:
            return 0
        try:
            return self.current_doc.GetType
        except Exception:
            return 0
