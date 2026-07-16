"""comtypes 桥接函数 - 将 pywin32 对象转换为 comtypes 接口

当 pywin32 IDispatch 调用某些 SW API 报 DISP_E_NONOPTIONAL_PARAM / 
TYPE_MISMATCH / DISP_E_EXCEPTION 时，需要用此桥接器转为 comtypes vtable 调用。
"""

import struct
from ctypes import cast as ct_cast, c_void_p, POINTER
import comtypes
import comtypes.client

SW_TLB = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\sldworks.tlb"


def load_sw_type_lib():
    """加载 SOLIDWORKS 类型库

    Returns:
        comtypes.gen.SldWorks 模块
    """
    try:
        comtypes.client.GetModule(SW_TLB)
        import comtypes.gen.SldWorks as sw_gen
        return sw_gen
    except Exception as e:
        print(f'加载类型库失败: {e}')
        return None


def bridge_to_comtypes(pywin32_obj, target_interface):
    """将 pywin32 PyIDispatch 桥接到 comtypes 类型化接口

    通过提取 PyIDispatch 内部 COM 指针（内存 offset 16），
    用 comtypes 包装为 IUnknown，再 QueryInterface 到目标接口。

    Args:
        pywin32_obj: pywin32 Dispatch 返回的对象
        target_interface: comtypes 目标接口类型（如 sw_gen.IFeatureManager）

    Returns:
        comtypes 类型化接口对象，失败返回 None
    """
    try:
        ole_obj = pywin32_obj._oleobj_
        obj_id = id(ole_obj)
        mem = (comtypes.c_byte * 64).from_address(obj_id)
        com_ptr = struct.unpack_from('<Q', mem, 16)[0]
        iunknown_ptr = ct_cast(c_void_p(com_ptr), POINTER(comtypes.IUnknown))
        iunknown_ptr.AddRef()
        return iunknown_ptr.QueryInterface(target_interface)
    except Exception as e:
        print(f'桥接失败: {e}')
        return None


def get_feature_manager_vtable(part_doc):
    """获取 FeatureManager 的 comtypes vtable 接口

    用于调用 FeatureCut3（26参）、FeatureRevolveCut2（10参）等
    IDispatch 不兼容的方法。

    Args:
        part_doc: pywin32 获取的 ModelDoc2 对象

    Returns:
        comtypes.gen.SldWorks.IFeatureManager 对象，失败返回 None
    """
    sw_gen = load_sw_type_lib()
    if sw_gen is None:
        return None

    fm = part_doc.FeatureManager
    return bridge_to_comtypes(fm, sw_gen.IFeatureManager)


def get_pack_and_go(part_doc):
    """获取 PackAndGo 接口

    Args:
        part_doc: pywin32 获取的 ModelDoc2 对象

    Returns:
        comtypes.gen.SldWorks.IPackAndGo 对象，失败返回 None
    """
    sw_gen = load_sw_type_lib()
    if sw_gen is None:
        return None

    pg = part_doc.GetPackAndGo
    if pg is None:
        return None
    return bridge_to_comtypes(pg, sw_gen.IPackAndGo)