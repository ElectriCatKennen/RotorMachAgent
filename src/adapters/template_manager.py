"""SolidWorks 模板配置管理系统

提供SW模板的搜索、选择和管理功能：
1. 从配置文件读取模板路径
2. 搜索系统默认模板目录
3. 支持自定义模板路径
4. 自动检测可用模板
5. 提供模板选择接口

配置文件格式见 data/templates/solidworks.json
"""

import os
import glob
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class TemplateInfo:
    """模板信息"""
    name: str
    path: str
    type: str          # part, assembly, drawing
    size: str = ""     # 图纸尺寸（仅工程图）
    description: str = ""


@dataclass
class TemplateConfig:
    """模板配置"""
    part_template: str = ""
    assembly_template: str = ""
    drawing_template: str = ""
    units: str = "mm"
    material: str = "45"
    color: str = "{192, 192, 192}"
    precision: float = 0.01
    annotation_scale: float = 1.0


class TemplateManager:
    """模板管理器"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.available_templates: Dict[str, List[TemplateInfo]] = {}
        self._scan_templates()

    def _load_config(self, config_path: str) -> dict:
        """加载模板配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        default_config = {
            "version": "1.0",
            "title": "SolidWorks 模板配置",
            "description": "SolidWorks 零件、装配体、工程图模板路径配置",
            "defaults": {
                "part_template": "",
                "assembly_template": "",
                "drawing_template": "",
                "units": "mm",
                "material": "45",
                "color": "{192, 192, 192}",
                "precision": 0.01,
                "annotation_scale": 1.0
            },
            "search_paths": [
                "C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2024\\templates",
                "C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2023\\templates",
                "C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2022\\templates",
                "C:\\Users\\Public\\Documents\\SOLIDWORKS\\SOLIDWORKS 2024\\templates",
                "C:\\Users\\Public\\Documents\\SOLIDWORKS\\SOLIDWORKS 2023\\templates",
                "C:\\Users\\Public\\Documents\\SOLIDWORKS\\SOLIDWORKS 2022\\templates",
                os.path.join(os.path.expanduser("~"), "Documents", "SOLIDWORKS", "templates")
            ],
            "template_patterns": {
                "part": [
                    "GB_Part*.prtdot",
                    "GB*part*.prtdot",
                    "Standard*.prtdot",
                    "Part*.prtdot"
                ],
                "assembly": [
                    "GB_Assembly*.asmdot",
                    "GB*assembly*.asmdot",
                    "Standard*.asmdot",
                    "Assembly*.asmdot"
                ],
                "drawing": [
                    "GB_Drawing*.drwdot",
                    "GB*drawing*.drwdot",
                    "A0*.drwdot",
                    "A1*.drwdot",
                    "A2*.drwdot",
                    "A3*.drwdot",
                    "A4*.drwdot",
                    "Standard*.drwdot",
                    "Drawing*.drwdot"
                ]
            },
            "custom_templates": {},
            "material_library": {
                "path": "",
                "search_paths": [
                    "C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2024\\materials",
                    "C:\\ProgramData\\SolidWorks\\SOLIDWORKS 2023\\materials",
                    "C:\\Users\\Public\\Documents\\SOLIDWORKS\\SOLIDWORKS 2024\\materials"
                ]
            }
        }
        return default_config

    def _scan_templates(self):
        """扫描所有可用模板"""
        self.available_templates = {
            "part": [],
            "assembly": [],
            "drawing": []
        }

        search_paths = self.config.get("search_paths", [])
        patterns = self.config.get("template_patterns", {})

        for template_type in ["part", "assembly", "drawing"]:
            type_patterns = patterns.get(template_type, [])
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue

                for pattern in type_patterns:
                    full_pattern = os.path.join(search_path, pattern)
                    files = glob.glob(full_pattern, recursive=False)
                    for file_path in files:
                        template_name = os.path.basename(file_path)
                        template_info = TemplateInfo(
                            name=template_name,
                            path=file_path,
                            type=template_type,
                            description=f"自动检测的{self._get_type_name(template_type)}模板"
                        )
                        if template_type == "drawing":
                            template_info.size = self._extract_drawing_size(template_name)

                        if template_info not in self.available_templates[template_type]:
                            self.available_templates[template_type].append(template_info)

        custom_templates = self.config.get("custom_templates", {})
        for template_type, templates in custom_templates.items():
            if template_type not in self.available_templates:
                self.available_templates[template_type] = []
            for name, path in templates.items():
                if os.path.exists(path):
                    template_info = TemplateInfo(
                        name=name,
                        path=path,
                        type=template_type,
                        description="用户自定义模板"
                    )
                    if template_type == "drawing":
                        template_info.size = self._extract_drawing_size(name)

                    if template_info not in self.available_templates[template_type]:
                        self.available_templates[template_type].append(template_info)

    def _get_type_name(self, template_type: str) -> str:
        """获取模板类型中文名称"""
        type_names = {
            "part": "零件",
            "assembly": "装配体",
            "drawing": "工程图"
        }
        return type_names.get(template_type, template_type)

    def _extract_drawing_size(self, file_name: str) -> str:
        """从文件名提取图纸尺寸"""
        size_map = {
            "A0": "A0",
            "A1": "A1",
            "A2": "A2",
            "A3": "A3",
            "A4": "A4",
            "a0": "A0",
            "a1": "A1",
            "a2": "A2",
            "a3": "A3",
            "a4": "A4"
        }
        for key, size in size_map.items():
            if key in file_name:
                return size
        return ""

    def get_available_templates(self, template_type: str) -> List[TemplateInfo]:
        """获取指定类型的可用模板列表
        
        Args:
            template_type: 模板类型：part, assembly, drawing
        
        Returns:
            List[TemplateInfo]: 模板信息列表
        """
        return self.available_templates.get(template_type, [])

    def select_template(self, template_type: str, criteria: dict = None) -> Optional[str]:
        """根据条件选择模板
        
        Args:
            template_type: 模板类型：part, assembly, drawing
            criteria: 选择条件，如 {"size": "A3"}
        
        Returns:
            Optional[str]: 选中的模板路径，若无匹配则返回None
        """
        templates = self.get_available_templates(template_type)
        
        if not templates:
            return None

        if criteria and template_type == "drawing" and "size" in criteria:
            target_size = criteria["size"]
            for template in templates:
                if template.size == target_size:
                    return template.path

        default_path = self.config.get("defaults", {}).get(f"{template_type}_template", "")
        if default_path and os.path.exists(default_path):
            return default_path

        if templates:
            return templates[0].path

        return None

    def set_custom_template(self, template_type: str, name: str, path: str):
        """设置自定义模板
        
        Args:
            template_type: 模板类型：part, assembly, drawing
            name: 模板名称
            path: 模板文件路径
        """
        if "custom_templates" not in self.config:
            self.config["custom_templates"] = {}
        if template_type not in self.config["custom_templates"]:
            self.config["custom_templates"][template_type] = {}
        
        self.config["custom_templates"][template_type][name] = path
        self._scan_templates()

    def save_config(self, config_path: str):
        """保存配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_default_config(self) -> TemplateConfig:
        """获取默认配置"""
        defaults = self.config.get("defaults", {})
        return TemplateConfig(
            part_template=defaults.get("part_template", ""),
            assembly_template=defaults.get("assembly_template", ""),
            drawing_template=defaults.get("drawing_template", ""),
            units=defaults.get("units", "mm"),
            material=defaults.get("material", "45"),
            color=defaults.get("color", "{192, 192, 192}"),
            precision=defaults.get("precision", 0.01),
            annotation_scale=defaults.get("annotation_scale", 1.0)
        )

    def set_default_template(self, template_type: str, path: str):
        """设置默认模板路径
        
        Args:
            template_type: 模板类型：part, assembly, drawing
            path: 模板文件路径
        """
        if "defaults" not in self.config:
            self.config["defaults"] = {}
        self.config["defaults"][f"{template_type}_template"] = path

    def add_search_path(self, path: str):
        """添加模板搜索路径
        
        Args:
            path: 搜索路径
        """
        if path not in self.config.get("search_paths", []):
            self.config["search_paths"].append(path)
            self._scan_templates()

    def print_available_templates(self):
        """打印所有可用模板"""
        print("=" * 60)
        print("可用模板列表")
        print("=" * 60)

        for template_type in ["part", "assembly", "drawing"]:
            templates = self.get_available_templates(template_type)
            type_name = self._get_type_name(template_type)
            
            print(f"\n【{type_name}模板】({len(templates)}个)")
            for i, template in enumerate(templates, 1):
                size_info = f" [{template.size}]" if template.size else ""
                print(f"  {i}. {template.name}{size_info}")
                print(f"     {template.path}")
                if template.description:
                    print(f"     描述: {template.description}")


def create_template_manager(config_path: str = None) -> TemplateManager:
    """创建模板管理器实例
    
    Args:
        config_path: 配置文件路径，默认从 data/templates/solidworks.json 加载
    
    Returns:
        TemplateManager 实例
    """
    if config_path is None:
        import importlib.resources
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, 'data', 'templates', 'solidworks.json')
        except Exception:
            config_path = None

    return TemplateManager(config_path)