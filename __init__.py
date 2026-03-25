import bpy
import bmesh
import mathutils
import os
from bpy_extras import view3d_utils
from collections import deque
import gpu
from gpu_extras.batch import batch_for_shader
import math

# ================= Translations (最完整国际化中英字典) =================
zh_dict = {
    # 面板与分类名
    ("*", "Little Prince 3D Part Splitter"): "小王子 3D拆件工作站",
    ("*", "PrintPrep"): "打印分件",
    
    # 模块 1-6 标题
    ("*", "1. Base Size & Position"): "1. 基础尺寸与定位",
    ("*", "2. Topology & Face Sets"): "2. 拓扑与面组规划",
    ("*", "3. Non-destructive Splitting"): "3. 无损拆解与提线",
    ("*", "4. Smart Cutter"): "4. 曲面智能切刀",
    ("*", "5. Smart Assembly Pegs"): "5. 智能防呆插销",
    ("*", "6. Boundary & Shell"): "6. 边界预处理与壳体",
    
    # === 所有属性和字段名 ===
    ("*", "Target Size (mm)"): "目标尺寸(mm)",
    ("*", "Uniform Scale"): "等比",  # 避开Blender原生的"Uniform(均匀)"翻译冲突
    ("*", "Merge Threshold"): "合并容差(mm)",
    ("*", "Decimate Ratio"): "精简比例",
    ("*", "Recalc Threshold"): "重分阈值",
    ("*", "Keep Top N"): "保留最大面组数量",
    ("*", "Island Threshold"): "最小面数阈值",
    ("*", "Auto Cap"): "拆分后自动封底",
    ("*", "Extract Boundaries"): "提边界线",
    ("*", "Cap Method"): "封底算法",
    ("*", "Line Output"): "线框输出",
    ("*", "Inner Scale"): "内圈缩放",
    ("*", "Inner Z Offset"): "内圈推移",
    ("*", "Outer Scale"): "外圈延展",
    ("*", "Outer Z Offset"): "外圈推移",
    ("*", "Thickness"): "切缝厚度",
    ("*", "Offset Dir"): "加厚方向",
    ("*", "Exact Boolean (Safe)"): "防溃精确布尔",
    ("*", "Segments (Anti-twist)"): "插销段数(防滑)",
    ("*", "Tolerance"): "装配公差",
    ("*", "Base Dia (Male)"): "底端直(公)",
    ("*", "Top Dia (Female)"): "顶端直(母)",
    ("*", "Total Length"): "插轴长",
    ("*", "Chamfer"): "端倒角",
    ("*", "Show Assembly List"): "展开装配列表",
    ("*", "Smooth Iterations"): "圆滑迭代",
    ("*", "Keep Ratio"): "精简保留",
    ("*", "Hollow Thickness"): "打孔厚度(mm)",
    
    # === 按钮/操作符名称 ===
    ("*", "Set Metric (mm)"): "环境转毫米",
    ("*", "Measure Tool Snap"): "卡尺吸附",
    ("*", "Absolute Scale"): "绝对缩放",
    ("*", "Drop to Floor"): "一键贴地",
    ("*", "Clean Debris"): "清洗碎渣",
    ("*", "Decimate Mesh"): "减面精简",
    ("*", "Regenerate Face Sets"): "重生面组",
    ("*", "Native Brush Mode"): "调用原生画笔修改",
    ("*", "Keep Large Parts"): "提取大块",
    ("*", "Clean Small Islands"): "清小孤岛",
    ("*", "Interactive Merge"): "射吸/融合面组",
    ("*", "Interactive Merge (Tool)"): "射吸/融合面组 (交互)",
    ("*", "Split Face Sets"): "色块一键全拆",
    ("*", "Interactive Peel"): "透视点选(剥离)",
    ("*", "Interactive Peel (Tool)"): "透视点选剥离 (交互)",
    ("*", "Extract Pure Boundaries"): "提纯净分割线",
    ("*", "Line to Cutter"): "线框转智能切刀",
    ("*", "Flip Cutter"): "批量反转切刀",
    ("*", "Multi-point Hand-drawn Cutter"): "无限加点手绘切刀",
    ("*", "Adjust Cutter"): "微调切刀",
    ("*", "Execute Cut & Locate"): "执行切割与圆心定位",
    ("*", "Convert to Smart Peg"): "转化为智能插销",
    ("*", "Add Peg on Surface"): "表面吸附打孔",
    ("*", "Flip Locator"): "反转方向",
    ("*", "Generate Preview"): "预览排版",
    ("*", "Execute Physical Assembly"): "物理装配执行",
    ("*", "Smooth Lines"): "平滑线框",
    ("*", "Smart Cap Holes"): "智能封底",
    ("*", "Extrude & Flatten"): "挤出压平",
    ("*", "Safe Flange Extrude"): "外扩法兰",
    ("*", "Boolean Hollow"): "抽壳掏空",

    # === 枚举下拉选项 ===
    ("*", "Max Axis"): "最大边", ("*", "X Axis"): "X轴", ("*", "Y Axis"): "Y轴", ("*", "Z Axis"): "Z轴",
    ("*", "Flat"): "平直", ("*", "Curved"): "平滑曲面",
    ("*", "Merged"): "合并", ("*", "Split"): "拆多段",
    ("*", "XY Level"): "XY水平", ("*", "XYZ Spherical"): "XYZ球面",
    ("*", "Center"): "双边居中", ("*", "Outward"): "向外", ("*", "Inward"): "向内",
    ("*", "Fuse to Male"): "融合进主件(一公多母)", ("*", "Independent Pegs"): "保留独立插销(双向打孔)",

    # === 极短提示词 ===
    ("*", "Flip"): "反转",
    ("*", "Cap (Flat)"): "封底(平)",
    ("*", "Cap (Curved)"): "封底(曲)",
    
    # === 动态拼装文本与提示 ===
    ("*", "Assembly List (Total {} Parts)"): "指派装配列表 (共 {} 散件)",
    ("*", "Male Part (Main)"): "公件(主件)",
    ("*", "Female Part {}"): "散件 {}",
    ("*", "Auto loading parts after cut..."): "切割后自动载入散件...",
    ("*", "✨ Custom Peg Active"): "✨ 当前为自定义智能插销",
    ("*", "Peg Tolerance (Only Active)"): "插销公差 (仅此项生效)",
    ("*", "Click Surface to Add Peg"): "点选表面生成插销",
    
    # === 物体命名与生成后缀 ===
    ("*", "_Split_Result"): "_分件结果",
    ("*", "_Backup_Hidden"): "_备份隐藏",
    ("*", "_Lines_Collection"): "分割线集合",
    ("*", "_Assembly_Result"): "_装配结果",
    
    # === 状态栏 / 报错交互提示 ===
    ("*", "Please select a mesh object first!"): "请先选中一个网格模型！",
    ("*", "Please select a mesh object first to convert!"): "请先选择要转化为插销的网格物体！",
    ("*", "Brush activation failed, please check Blender version. Error: {}"): "画笔激活失败，请检查Blender版本。错误: {}",
    ("*", "🖌️ Face Set brush activated!"): "🖌️ 面组画笔已激活！",
    ("*", "🔨 Interactive Merge: [Left Click] Pick/Fuse | [Alt+Left Click] Suck Color | [Right Click] Exit"): "🔨 交互合并：【左键】拾取/融合 | 【Alt+左键】吸取面组 | 【右键】退出",
    ("*", "🔨 Target Set picked: [{}] | [LClick] Fuse | [Alt+LClick] Suck | [RClick] Exit"): "🔨 目标面组已锁定为 [{}] | 【左键】融合 | 【Alt+左键】吸取 | 【右键】退出",
    ("*", "✂️ Interactive Peel: Left Click to select colors | Enter/Space to Confirm | Right Click to Cancel"): "✂️ 【透视选区剥离】左键点选你想单独拆出来的色块 (可多选) | 按【回车键 / 空格】确认拆分 | 右键取消",
    ("*", "✂️ Selected {} blocks | Press [Enter] to split | [Right Click] to Cancel"): "✂️ 【透视选区剥离】已选中 {} 个色块 | 按【回车/空格】确认拆分 | 右键取消",
    ("*", "🖋️ [Hand-drawn Cutter] Left Click surface | MMB rotate | Right Click/ESC Generate"): "🖋️ 【手绘切刀】左键点击表面加点 | 鼠标中键旋转视角 | 【右键/ESC】生成切刀",
    ("*", "🚀 Press G to move, SPACE/ENTER to Confirm!"): "🚀 【切刀生成完成】按 G 微调位置/大小，按【空格/回车】结束确认！",
    ("*", "🔨 Click surface to locate peg | MMB rotate | RClick/ESC exit"): "🔨 表面点击定位插销 | 鼠标中键旋转 | 【右键/Esc】退出",
    ("*", "Points < 3, cancelled."): "点数不足3个，已取消生成。",
    ("*", "Batch cut and locate successful!"): "批量切割并自动识别装配列表完毕！",
    ("*", "Converted {} objects to custom pegs!"): "成功将 {} 个物体转化为智能插销 (仅公差生效)！",
    ("*", "Batch assembly executed!"): "批量装配已完美执行！",
    
    # === 撤销历史 (Undo History) ===
    ("*", "Apply Cutter"): "应用切刀",
    ("*", "Undo: Clean Small Islands"): "清孤岛面组",
    ("*", "Undo: Keep Large Parts"): "提取大块面组",
    ("*", "Undo: Smooth Lines"): "平滑精简线框",
    ("*", "Undo: Split Face Sets"): "一键全拆并保留材质"
}

translations_dict = {
    "zh_HANS": zh_dict,  # 适配 Blender 4.x 最新中文代号
    "zh_CN": zh_dict,    # 适配 Blender 旧版中文代号，双保险
}

# ================= Helper Functions =================
def T(text):
    """暴力强制翻译函数：直接拦截并替换UI上即将渲染的英文字符"""
    try:
        return bpy.app.translations.pgettext_iface(text)
    except:
        return text

def get_bu(context, mm_value):
    return mm_value / (context.scene.unit_settings.scale_length * 1000.0)

def safe_remove_object(obj):
    if not obj: return
    mesh = obj.data if obj.type == 'MESH' else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh and mesh.users == 0: bpy.data.meshes.remove(mesh, do_unlink=True)

def apply_modifier_safely(obj, mod_name):
    mod = obj.modifiers.get(mod_name)
    if not mod: return False
    try:
        bpy.ops.object.modifier_apply(modifier=mod_name)
        return True
    except Exception as e:
        if mod.type == 'BOOLEAN' and mod.solver == 'EXACT':
            print(f"⚠️ [Fallback] {obj.name} EXACT boolean failed, trying FAST...")
            mod.solver = 'FAST'
            try:
                bpy.ops.object.modifier_apply(modifier=mod_name)
                return True
            except Exception as e2: return False
        return False

def move_to_collection(objs, col_name, context, hide_col=False):
    if not objs: return
    target_col = bpy.data.collections.get(col_name)
    if not target_col:
        target_col = bpy.data.collections.new(col_name)
        context.scene.collection.children.link(target_col)
    if hide_col: target_col.hide_viewport = True
    for obj in objs:
        for c in obj.users_collection: c.objects.unlink(obj)
        target_col.objects.link(obj)

# ================= Object Sync Engine =================
def update_single_cutter_geo(self, context):
    if "_Cutter" in self.name and self.type == 'MESH':
        rebuild_ez_cutter(context, self, self.ez_cutter_inner_scale, self.ez_cutter_inner_z, self.ez_cutter_outer_z, self.ez_cutter_outer_scale)
        if self == context.active_object:
            for obj in context.selected_objects:
                if obj != self and "_Cutter" in obj.name and obj.type == 'MESH':
                    if obj.ez_cutter_inner_scale != self.ez_cutter_inner_scale: obj.ez_cutter_inner_scale = self.ez_cutter_inner_scale
                    if obj.ez_cutter_inner_z != self.ez_cutter_inner_z: obj.ez_cutter_inner_z = self.ez_cutter_inner_z
                    if obj.ez_cutter_outer_scale != self.ez_cutter_outer_scale: obj.ez_cutter_outer_scale = self.ez_cutter_outer_scale
                    if obj.ez_cutter_outer_z != self.ez_cutter_outer_z: obj.ez_cutter_outer_z = self.ez_cutter_outer_z

def update_single_cutter_mod(self, context):
    if "_Cutter" in self.name and self.type == 'MESH':
        mod = self.modifiers.get("Thickness")
        if not mod: mod = self.modifiers.get("切割厚度")
        if mod and mod.type == 'SOLIDIFY':
            mod.thickness, mod.offset = get_bu(context, self.ez_cutter_thickness), float(self.ez_cutter_offset)
        if self == context.active_object:
            for obj in context.selected_objects:
                if obj != self and "_Cutter" in obj.name and obj.type == 'MESH':
                    if obj.ez_cutter_thickness != self.ez_cutter_thickness: obj.ez_cutter_thickness = self.ez_cutter_thickness
                    if obj.ez_cutter_offset != self.ez_cutter_offset: obj.ez_cutter_offset = self.ez_cutter_offset

def update_single_peg(self, context):
    if "_Peg_Preview" in self.name and self.type == 'MESH':
        if self.get("is_custom_peg"):
            if self == context.active_object:
                for obj in context.selected_objects:
                    if obj != self and "_Peg_Preview" in obj.name and obj.get("is_custom_peg"):
                        if obj.ez_peg_tolerance != self.ez_peg_tolerance: obj.ez_peg_tolerance = self.ez_peg_tolerance
            return

        L, r_base, r_top, segs = self.ez_peg_length, self.ez_peg_dia_base / 2.0, self.ez_peg_dia_top / 2.0, self.ez_peg_segments
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=get_bu(context, r_base), radius2=get_bu(context, r_top), depth=get_bu(context, L))
        new_mesh = bpy.data.meshes.new("EZ_Peg_Preview_Mesh")
        bm.to_mesh(new_mesh)
        bm.free()
        old_mesh = self.data
        self.data = new_mesh
        if old_mesh and old_mesh.users == 0: bpy.data.meshes.remove(old_mesh, do_unlink=True)
        loc_name = self.name.replace("_Peg_Preview", "_Locator")
        if loc_name in bpy.data.objects: self.matrix_world = bpy.data.objects[loc_name].matrix_world 
        if "Chamfer" in self.modifiers: self.modifiers["Chamfer"].width = get_bu(context, self.ez_peg_chamfer)
        elif self.ez_peg_chamfer > 0:
            bevel = self.modifiers.new("Chamfer", 'BEVEL')
            bevel.width, bevel.segments, bevel.limit_method, bevel.angle_limit = get_bu(context, self.ez_peg_chamfer), 1, 'ANGLE', 0.785398
        
        is_active = (self == context.active_object) or (loc_name == getattr(context.active_object, "name", ""))
        if is_active:
            for obj in context.selected_objects:
                target_peg = obj if "_Peg_Preview" in obj.name else (bpy.data.objects.get(obj.name.replace("_Locator", "_Peg_Preview")) if "_Locator" in obj.name else None)
                if target_peg and target_peg != self and not target_peg.get("is_custom_peg"):
                    if target_peg.ez_peg_segments != self.ez_peg_segments: target_peg.ez_peg_segments = self.ez_peg_segments
                    if target_peg.ez_peg_dia_base != self.ez_peg_dia_base: target_peg.ez_peg_dia_base = self.ez_peg_dia_base
                    if target_peg.ez_peg_dia_top != self.ez_peg_dia_top: target_peg.ez_peg_dia_top = self.ez_peg_dia_top
                    if target_peg.ez_peg_length != self.ez_peg_length: target_peg.ez_peg_length = self.ez_peg_length
                    if target_peg.ez_peg_chamfer != self.ez_peg_chamfer: target_peg.ez_peg_chamfer = self.ez_peg_chamfer
                    if target_peg.ez_peg_tolerance != self.ez_peg_tolerance: target_peg.ez_peg_tolerance = self.ez_peg_tolerance

# ================= Core Mesh Operators =================
def perform_capping(obj, method):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True)
    if method == 'FLAT':
        bpy.ops.mesh.fill_holes(sides=0)
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    elif method == 'CURVED':
        bpy.ops.mesh.fill()
        bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=2)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

def rebuild_ez_cutter(context, obj, inner_scale=0.85, inner_z_offset=0.0, outer_z_offset=0.0, outer_scale=1.2):
    mesh = obj.data
    total_verts = len(mesh.vertices)
    if total_verts < 10 or (total_verts - 1) % 3 != 0: return
    M = (total_verts - 1) // 3
    mat_world = obj.matrix_world
    mid_world_pts = [mat_world @ v.co for v in mesh.vertices[M:2*M]]
    center = sum(mid_world_pts, mathutils.Vector()) / M
    normal = mathutils.Vector((0.0, 0.0, 0.0))
    for i in range(M):
        v_curr, v_next = mid_world_pts[i], mid_world_pts[(i + 1) % M]
        normal.x += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
        normal.y += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
        normal.z += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)
    normal = mathutils.Vector((0, 0, 1)) if normal.length < 1e-6 else normal.normalized()
    matrix_world = mathutils.Matrix.LocRotScale(center, normal.to_track_quat('Z', 'Y'), None)
    matrix_inv = matrix_world.inverted()
    local_mid = [matrix_inv @ p for p in mid_world_pts]
    R_inner = min(math.sqrt(p.x2 + p.y2) for p in local_mid) * inner_scale
    outer_z_bu, inner_z_bu = get_bu(context, outer_z_offset), get_bu(context, inner_z_offset)
    local_inner, local_outer = [], []
    for p in local_mid:
        mag = math.sqrt(p.x2 + p.y2)
        lx, ly = ((p.x / mag) * R_inner, (p.y / mag) * R_inner) if mag > 1e-6 else (0.0, 0.0)
        local_inner.append(mathutils.Vector((lx, ly, inner_z_bu)))
        local_outer.append(mathutils.Vector((p.x * outer_scale, p.y * outer_scale, p.z + outer_z_bu)))
    obj.matrix_world = matrix_world
    for i in range(M):
        mesh.vertices[i].co, mesh.vertices[M + i].co, mesh.vertices[2 * M + i].co = local_inner[i], local_mid[i], local_outer[i]
    mesh.vertices[3 * M].co = mathutils.Vector((0, 0, inner_z_bu))
    mesh.update()

# ================= Global Properties =================
class ObjectPointerItem(bpy.types.PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)

class PrintSplitterV08Properties(bpy.types.PropertyGroup):
    target_dimension: bpy.props.FloatProperty(name="Target Size (mm)", default=100.0, min=0.1, max=10000.0)
    scale_axis: bpy.props.EnumProperty(items=[('MAX', "Max Axis", ""), ('X', "X Axis", ""), ('Y', "Y Axis", ""), ('Z', "Z Axis", "")], default='MAX')
    is_uniform: bpy.props.BoolProperty(name="Uniform Scale", default=True) # 修改为Uniform Scale
    recalc_threshold: bpy.props.FloatProperty(name="Recalc Threshold", default=0.99, min=0.01, max=1.0)
    top_n_count: bpy.props.IntProperty(name="Keep Top N", default=20, min=1, max=1000)
    min_face_count: bpy.props.IntProperty(name="Island Threshold", default=50, min=1, max=50000)
    auto_cap: bpy.props.BoolProperty(name="Auto Cap", default=True)
    cap_method: bpy.props.EnumProperty(items=[('FLAT', "Flat", ""), ('CURVED', "Curved", "")], default='FLAT')
    keep_boundary: bpy.props.BoolProperty(name="Extract Boundaries", default=True)
    line_output_mode: bpy.props.EnumProperty(items=[('MERGED', "Merged", ""), ('SPLIT', "Split", "")], default='SPLIT')
    hollow_thickness: bpy.props.FloatProperty(name="Hollow Thickness", default=2.0, min=0.1, max=20.0)
    smooth_iterations: bpy.props.IntProperty(name="Smooth Iterations", default=10, min=0, max=200)
    line_decimate_ratio: bpy.props.FloatProperty(name="Keep Ratio", default=1.0, min=0.01, max=1.0, subtype='PERCENTAGE')
    flange_mode: bpy.props.EnumProperty(items=[('XY', "XY Level", ""), ('XYZ', "XYZ Spherical", "")], default='XY')
    clean_merge_distance: bpy.props.FloatProperty(name="Merge Threshold", default=0.1, min=0.0001, max=10.0)
    decimate_ratio: bpy.props.FloatProperty(name="Decimate Ratio", default=0.5, min=0.01, max=1.0, subtype='PERCENTAGE')
    use_exact_bool: bpy.props.BoolProperty(name="Exact Boolean (Safe)", default=True)
    target_mesh_name: bpy.props.StringProperty()
    
    cutter_inner_scale: bpy.props.FloatProperty(name="Inner Scale", default=0.85, min=0.01, max=2.0)
    cutter_inner_z_offset: bpy.props.FloatProperty(name="Inner Z Offset", default=0.0, min=-50.0, max=50.0)
    cutter_outer_scale: bpy.props.FloatProperty(name="Outer Scale", default=1.3, min=1.01, max=10.0)
    cutter_outer_z_offset: bpy.props.FloatProperty(name="Outer Z Offset", default=0.0, min=-50.0, max=50.0)
    cutter_thickness: bpy.props.FloatProperty(name="Thickness", default=0.5, min=0.01, max=500.0)
    cutter_offset: bpy.props.EnumProperty(name="Offset Dir", items=[('0', "Center", ""), ('1', "Outward", ""), ('-1', "Inward", "")], default='0')
    
    ez_peg_segments: bpy.props.IntProperty(name="Segments (Anti-twist)", default=6, min=3, max=64)
    ez_peg_dia_base: bpy.props.FloatProperty(name="Base Dia (Male)", default=10.0, min=0.1, max=500.0)
    ez_peg_dia_top: bpy.props.FloatProperty(name="Top Dia (Female)", default=8.0, min=0.1, max=500.0)
    ez_peg_length: bpy.props.FloatProperty(name="Total Length", default=20.0, min=1.0, max=1000.0)
    ez_peg_chamfer: bpy.props.FloatProperty(name="Chamfer", default=0.6, min=0.0, max=5.0)
    ez_peg_tolerance: bpy.props.FloatProperty(name="Tolerance", default=0.2, min=0.0, max=5.0, step=0.05)
    
    show_peg_list: bpy.props.BoolProperty(name="Show Assembly List", default=False)
    peg_male_obj: bpy.props.PointerProperty(type=bpy.types.Object)
    peg_females: bpy.props.CollectionProperty(type=ObjectPointerItem)
    peg_assembly_mode: bpy.props.EnumProperty(items=[('FUSE', "Fuse to Male", ""), ('INDEPENDENT', "Independent Pegs", "")], default='FUSE')

# ================= Module: Operators =================
class PRINTPREP_V08_OT_setup_units(bpy.types.Operator):
    bl_idname = "printprep_v08.setup_units"
    bl_label = "Set Metric (mm)"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        context.scene.unit_settings.system, context.scene.unit_settings.length_unit, context.scene.unit_settings.scale_length = 'METRIC', 'MILLIMETERS', 0.001
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D': space.clip_start, space.clip_end, space.overlay.grid_scale = 0.1, 100000.0, 0.001
        context.view_layer.update()
        return {'FINISHED'}

class PRINTPREP_V08_OT_measure_tool(bpy.types.Operator):
    bl_idname = "printprep_v08.measure_tool"
    bl_label = "Measure Tool Snap"
    bl_options = {'REGISTER'}
    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.measure")
        context.scene.tool_settings.use_snap, context.scene.tool_settings.snap_elements = True, {'VERTEX'}
        return {'FINISHED'}

class PRINTPREP_V08_OT_absolute_scale(bpy.types.Operator):
    bl_idname = "printprep_v08.absolute_scale"
    bl_label = "Absolute Scale"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        original_selection = [o for o in context.selected_objects if o.type == 'MESH']
        if not original_selection: return {'CANCELLED'}
        props = context.scene.print_splitter_v08_props
        unit_scale = context.scene.unit_settings.scale_length
        for obj in original_selection:
            if len(obj.data.vertices) < 4: continue 
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            d = obj.dimensions
            if props.scale_axis == 'MAX':
                axis = 0 if d.x >= d.y and d.x >= d.z else (1 if d.y >= d.x and d.y >= d.z else 2)
                current_bu = max(d)
            else:
                axis = ['x','y','z'].index(props.scale_axis.lower())
                current_bu = getattr(d, props.scale_axis.lower())
                
            if current_bu < 0.000001: continue
            factor = props.target_dimension / (current_bu * unit_scale * 1000.0)
            
            if props.is_uniform: obj.scale *= factor
            else: obj.scale[axis] *= factor
            
            if obj.data.users > 1: obj.data = obj.data.copy()
            try: bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            except Exception as e: pass
        for obj in original_selection: obj.select_set(True)
        if original_selection: context.view_layer.objects.active = original_selection[0]
        bpy.ops.ed.undo_push(message=T("Absolute Scale"))
        return {'FINISHED'}

class CUT_OT_clean_mesh(bpy.types.Operator):
    bl_idname = "cut.clean_mesh"
    bl_label = "Clean Debris"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not objs: return {'CANCELLED'}
        for obj in objs:
            if len(obj.data.vertices) < 4: continue
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=context.scene.print_splitter_v08_props.clean_merge_distance)
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.ed.undo_push(message=T("Clean Debris"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_decimate_mesh(bpy.types.Operator):
    bl_idname = "printprep_v08.decimate_mesh"
    bl_label = "Decimate Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.print_splitter_v08_props
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                context.view_layer.objects.active = obj
                mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
                mod.ratio = props.decimate_ratio
                apply_modifier_safely(obj, mod.name)
        bpy.ops.ed.undo_push(message=T("Decimate Mesh"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_recalc_face_sets(bpy.types.Operator):
    bl_idname = "printprep_v08.recalc_face_sets"
    bl_label = "Regenerate Face Sets"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        for obj in objs:
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='SCULPT')
            try: bpy.ops.sculpt.face_sets_init(mode='NORMALS', threshold=context.scene.print_splitter_v08_props.recalc_threshold)
            except Exception as e: pass
            bpy.ops.object.mode_set(mode='OBJECT')
        if objs: context.view_layer.objects.active = objs[-1]; bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.ed.undo_push(message=T("Regenerate Face Sets"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_enter_brush_mode(bpy.types.Operator):
    bl_idname = "printprep_v08.enter_brush_mode"
    bl_label = "Native Brush Mode"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH': 
            self.report({'WARNING'}, T("Please select a mesh object first!"))
            return {'CANCELLED'}
        if context.mode != 'SCULPT': bpy.ops.object.mode_set(mode='SCULPT')
        if '.sculpt_face_set' not in obj.data.attributes:
            try: bpy.ops.sculpt.face_sets_init(mode='NORMALS', threshold=0.9)
            except: pass
        try: 
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.draw_face_sets")
            self.report({'INFO'}, T("🖌️ Face Set brush activated!"))
        except Exception:
            try: 
                bpy.ops.wm.tool_set_by_id(name="builtin.brush.Draw Face Sets")
                self.report({'INFO'}, T("🖌️ Face Set brush activated!"))
            except Exception as e: 
                self.report({'WARNING'}, T("Brush activation failed, please check Blender version. Error: {}").format(str(e)))
                return {'CANCELLED'}
        return {'FINISHED'}

class PRINTPREP_V08_OT_keep_top_n(bpy.types.Operator):
    bl_idname = "printprep_v08.keep_top_n"
    bl_label = "Keep Large Parts"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        props = context.scene.print_splitter_v08_props
        for obj in objs:
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = obj.data
            if '.sculpt_face_set' not in mesh.attributes: continue
            fs_attr = mesh.attributes['.sculpt_face_set'].data
            fs_values = [p.value for p in fs_attr]
            fs_counts = {}
            for val in fs_values: fs_counts[val] = fs_counts.get(val, 0) + 1
            sorted_fs = sorted(fs_counts.items(), key=lambda x: x[1], reverse=True)
            target_fs_ids = set(k for k, v in sorted_fs[:props.top_n_count])
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            queue = deque()
            for f in bm.faces:
                if fs_values[f.index] in target_fs_ids:
                    for edge in f.edges:
                        for lf in edge.link_faces:
                            if fs_values[lf.index] not in target_fs_ids: 
                                queue.append(f.index)
                                break
            while queue:
                curr_idx = queue.popleft()
                curr_fs = fs_values[curr_idx]
                for edge in bm.faces[curr_idx].edges:
                    for lf in edge.link_faces:
                        if fs_values[lf.index] not in target_fs_ids:
                            fs_values[lf.index] = curr_fs
                            queue.append(lf.index)
            largest_fs = sorted_fs[0][0]
            for i in range(len(fs_values)):
                if fs_values[i] not in target_fs_ids: fs_values[i] = largest_fs
            for i, p in enumerate(fs_attr): p.value = fs_values[i]
            bm.free()
            mesh.update()
            bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.ed.undo_push(message=T("Undo: Keep Large Parts"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_clean_by_threshold(bpy.types.Operator):
    bl_idname = "printprep_v08.clean_by_threshold"
    bl_label = "Clean Small Islands"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        props = context.scene.print_splitter_v08_props
        for obj in objs:
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            mesh = obj.data
            if '.sculpt_face_set' not in mesh.attributes: continue
            fs_attr = mesh.attributes['.sculpt_face_set'].data
            fs_values = [p.value for p in fs_attr]
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            visited, small_islands = set(), []
            for f in bm.faces:
                if f.index not in visited:
                    island_faces, stack, my_fs = [], [f], fs_values[f.index]
                    visited.add(f.index)
                    while stack:
                        curr = stack.pop()
                        island_faces.append(curr.index)
                        for edge in curr.edges:
                            for lf in edge.link_faces:
                                if lf.index not in visited and fs_values[lf.index] == my_fs:
                                    visited.add(lf.index); stack.append(lf)
                    if len(island_faces) <= props.min_face_count: small_islands.append({"faces": island_faces})
            small_islands.sort(key=lambda x: len(x["faces"]))
            for isl in small_islands:
                neighbor_fs_counts = {}
                for f_idx in isl["faces"]:
                    for edge in bm.faces[f_idx].edges:
                        for lf in edge.link_faces:
                            if lf.index not in isl["faces"]:
                                out_fs = fs_values[lf.index]
                                neighbor_fs_counts[out_fs] = neighbor_fs_counts.get(out_fs, 0) + 1
                if neighbor_fs_counts:
                    best_neighbor_fs = max(neighbor_fs_counts, key=neighbor_fs_counts.get)
                    for f_idx in isl["faces"]: fs_values[f_idx] = best_neighbor_fs
            for i, p in enumerate(fs_attr): p.value = fs_values[i]
            bm.free()
            mesh.update()
            bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.ed.undo_push(message=T("Undo: Clean Small Islands"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_interactive_merge(bpy.types.Operator):
    bl_idname = "printprep_v08.interactive_merge"
    bl_label = "Interactive Merge"
    bl_options = {'REGISTER', 'UNDO'}
    target_fs_id: bpy.props.IntProperty(default=-1)

    def invoke(self, context, event):
        obj = context.active_object
        if obj is None or obj.type != 'MESH': 
            self.report({'WARNING'}, T("Please select a mesh object first!"))
            return {'CANCELLED'}
        if context.mode != 'SCULPT': bpy.ops.object.mode_set(mode='SCULPT')
        if '.sculpt_face_set' not in obj.data.attributes:
            try: bpy.ops.sculpt.face_sets_init(mode='NORMALS', threshold=0.9)
            except: pass
        self.target_fs_id = -1
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(T("🔨 Interactive Merge: [Left Click] Pick/Fuse | [Alt+Left Click] Suck Color | [Right Click] Exit"))
        return {'RUNNING_MODAL'}
    def cancel(self, context): context.area.header_text_set(None)
    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            return {'FINISHED'}
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'} or (event.type in {'MOUSEMOVE'} and event.value != 'PRESS'): return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            coord = event.mouse_region_x, event.mouse_region_y
            region, rv3d = context.region, context.region_data
            view_vector, ray_origin = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord), view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            obj = context.active_object
            matrix_inv = obj.matrix_world.inverted()
            success, loc, normal, poly_index = obj.ray_cast(matrix_inv @ ray_origin, matrix_inv @ (ray_origin + view_vector * 10000) - matrix_inv @ ray_origin)
            if success and '.sculpt_face_set' in obj.data.attributes:
                bpy.ops.ed.undo_push(message=T("Interactive Merge"))
                fs_attr = obj.data.attributes['.sculpt_face_set'].data
                clicked_fs_id = fs_attr[poly_index].value
                if event.alt:
                    self.target_fs_id = clicked_fs_id
                    context.area.header_text_set(T("🔨 Target Set picked: [{}] | [LClick] Fuse | [Alt+LClick] Suck | [RClick] Exit").format(self.target_fs_id))
                else:
                    if self.target_fs_id == -1:
                        self.target_fs_id = clicked_fs_id
                        context.area.header_text_set(T("🔨 Target Set picked: [{}] | [LClick] Fuse | [Alt+LClick] Suck | [RClick] Exit").format(self.target_fs_id))
                    elif clicked_fs_id != self.target_fs_id:
                        fs_values = [p.value for p in fs_attr]
                        for i in range(len(fs_values)):
                            if fs_values[i] == clicked_fs_id: fs_values[i] = self.target_fs_id
                        for i, p in enumerate(fs_attr): p.value = fs_values[i]
                        obj.data.update()
                        bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.mode_set(mode='SCULPT')
        return {'RUNNING_MODAL'}

class PRINTPREP_V08_OT_interactive_split(bpy.types.Operator):
    bl_idname = "printprep_v08.interactive_split"
    bl_label = "Interactive Peel"
    bl_options = {'REGISTER', 'UNDO'}
    def invoke(self, context, event):
        obj = context.active_object
        if obj is None or obj.type != 'MESH': return {'CANCELLED'}
        if context.mode != 'SCULPT': bpy.ops.object.mode_set(mode='SCULPT')
        self.selected_fs = set()
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(T("✂️ Interactive Peel: Left Click to select colors | Enter/Space to Confirm | Right Click to Cancel"))
        return {'RUNNING_MODAL'}
    def cancel(self, context): context.area.header_text_set(None)
    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'} or event.shift or event.ctrl or event.type.startswith('NUMPAD'): return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'}: 
            context.area.header_text_set(None)
            return {'FINISHED'}
        if event.type in {'RET', 'NUMPAD_ENTER', 'SPACE'} and event.value == 'PRESS':
            context.area.header_text_set(None)
            if not self.selected_fs: return {'FINISHED'}
            bpy.ops.printprep_v08.split_face_sets(split_mode='SELECTED', selected_fs_str=",".join(map(str, self.selected_fs)))
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            coord = event.mouse_region_x, event.mouse_region_y
            region, rv3d = context.region, context.region_data
            view_vector, ray_origin = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord), view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            obj = context.active_object
            matrix_inv = obj.matrix_world.inverted()
            success, loc, normal, poly_index = obj.ray_cast(matrix_inv @ ray_origin, matrix_inv @ (ray_origin + view_vector * 10000) - matrix_inv @ ray_origin)
            if success and '.sculpt_face_set' in obj.data.attributes:
                fs_val = obj.data.attributes['.sculpt_face_set'].data[poly_index].value
                if fs_val in self.selected_fs: self.selected_fs.remove(fs_val)
                else: self.selected_fs.add(fs_val)
                context.area.header_text_set(T("✂️ Selected {} blocks | Press [Enter] to split | [Right Click] to Cancel").format(len(self.selected_fs)))
        return {'RUNNING_MODAL'}

class PRINTPREP_V08_OT_split_face_sets(bpy.types.Operator):
    bl_idname = "printprep_v08.split_face_sets"
    bl_label = "Split Face Sets"
    bl_options = {'REGISTER', 'UNDO'}
    split_mode: bpy.props.EnumProperty(items=[('ALL', 'All', ''), ('SELECTED', 'Selected', '')], default='ALL')
    selected_fs_str: bpy.props.StringProperty(default="")
    def execute(self, context):
        original_objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not original_objs: return {'CANCELLED'}
        props = context.scene.print_splitter_v08_props
        bpy.ops.object.mode_set(mode='OBJECT')
        all_separated_objs = []
        for original_obj in original_objs:
            context.view_layer.objects.active = original_obj
            mesh = original_obj.data
            if '.sculpt_face_set' not in mesh.attributes: continue
            if props.keep_boundary and self.split_mode == 'ALL': 
                bpy.ops.printprep_v08.extract_boundaries_only()
                bpy.ops.object.select_all(action='DESELECT')
                original_obj.select_set(True)
                context.view_layer.objects.active = original_obj

            new_obj = original_obj.copy()
            new_obj.data = original_obj.data.copy()
            context.collection.objects.link(new_obj)
            orig_mats = [m for m in new_obj.data.materials]
            orig_mat_indices = [p.material_index for p in new_obj.data.polygons]
            if 'orig_mat_idx' not in new_obj.data.attributes: new_obj.data.attributes.new(name='orig_mat_idx', type='INT', domain='FACE')
            new_obj.data.attributes['orig_mat_idx'].data.foreach_set("value", orig_mat_indices)

            bpy.ops.object.select_all(action='DESELECT')
            new_obj.select_set(True)
            context.view_layer.objects.active = new_obj
            source_obj = new_obj
            mesh = source_obj.data
            try:
                fs_values = [0] * len(mesh.polygons)
                mesh.attributes['.sculpt_face_set'].data.foreach_get("value", fs_values)
                unique_fs = set(fs_values)
                fs_to_mat_idx = {}
                if self.split_mode == 'SELECTED' and self.selected_fs_str:
                    target_ids = set(int(x) for x in self.selected_fs_str.split(',') if x)
                    mat_counter = 1
                    for val in unique_fs:
                        if val in target_ids: 
                            fs_to_mat_idx[val] = mat_counter
                            mat_counter += 1
                        else: fs_to_mat_idx[val] = 0 
                else: fs_to_mat_idx = {val: i for i, val in enumerate(unique_fs)}
                source_obj.data.materials.clear()
                for _ in range(max(fs_to_mat_idx.values() if fs_to_mat_idx else {0}) + 1): source_obj.data.materials.append(bpy.data.materials.new(name="Temp_Split_Mat"))
                new_mat_indices = [fs_to_mat_idx[val] for val in fs_values]
                mesh.polygons.foreach_set("material_index", new_mat_indices)
                mesh.update()
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='MATERIAL')
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception as e:
                safe_remove_object(source_obj)
                continue

            separated_objs = context.selected_objects[:]
            bpy.ops.object.select_all(action='DESELECT')
            for idx, final_obj in enumerate(separated_objs):
                context.view_layer.objects.active = final_obj
                final_obj.select_set(True)
                final_obj.name = f"{original_obj.name}_Part_{idx+1:02d}"
                final_obj.data.materials.clear()
                for m in orig_mats: final_obj.data.materials.append(m)
                if 'orig_mat_idx' in final_obj.data.attributes:
                    restored_indices = [0] * len(final_obj.data.polygons)
                    final_obj.data.attributes['orig_mat_idx'].data.foreach_get("value", restored_indices)
                    final_obj.data.polygons.foreach_set("material_index", restored_indices)
                    final_obj.data.attributes.remove(final_obj.data.attributes['orig_mat_idx'])
                if props.auto_cap: perform_capping(final_obj, props.cap_method)
                final_obj.select_set(False)
                all_separated_objs.append(final_obj)
                
            move_to_collection(all_separated_objs, f"{original_obj.name}{T('_Split_Result')}", context)
            move_to_collection([original_obj], f"{original_obj.name}{T('_Backup_Hidden')}", context, hide_col=True)
            
        for safe_obj in all_separated_objs: safe_obj.select_set(True)
        bpy.ops.ed.undo_push(message=T("Undo: Split Face Sets"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_extract_boundaries_only(bpy.types.Operator):
    bl_idname = "printprep_v08.extract_boundaries_only"
    bl_label = "Extract Pure Boundaries"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not objs: return {'CANCELLED'}
        props = context.scene.print_splitter_v08_props
        bpy.ops.object.mode_set(mode='OBJECT')
        all_lines_objs = []
        for obj in objs:
            mesh = obj.data
            if '.sculpt_face_set' not in mesh.attributes: continue
            fs_values = [p.value for p in mesh.attributes['.sculpt_face_set'].data]
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bm.edges.ensure_lookup_table()
            edges_to_keep, used_verts = [], set()
            for e in bm.edges:
                if len(e.link_faces) > 1:
                    fs1 = fs_values[e.link_faces[0].index]
                    for lf in e.link_faces[1:]:
                        if fs_values[lf.index] != fs1: 
                            edges_to_keep.append(e)
                            used_verts.add(e.verts[0]); used_verts.add(e.verts[1])
                            break
            if not edges_to_keep: 
                bm.free()
                continue
            vert_map, new_verts = {}, []
            for v in used_verts:
                vert_map[v] = len(new_verts)
                new_verts.append(v.co.copy())
            new_edges = [(vert_map[e.verts[0]], vert_map[e.verts[1]]) for e in edges_to_keep]
            bm.free()
            new_mesh = bpy.data.meshes.new(f"Lines_{obj.name}")
            new_mesh.from_pydata(new_verts, new_edges, [])
            new_mesh.update()
            lines_obj = bpy.data.objects.new(f"Lines_{obj.name}", new_mesh)
            lines_obj.matrix_world = obj.matrix_world
            move_to_collection([lines_obj], T("_Lines_Collection"), context)
            all_lines_objs.append(lines_obj)
        if not all_lines_objs: return {'CANCELLED'}
        if props.line_output_mode == 'SPLIT':
            bpy.ops.object.select_all(action='DESELECT')
            for lines_obj in all_lines_objs: lines_obj.select_set(True)
            context.view_layer.objects.active = all_lines_objs[0]
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class CUT_OT_line_to_cutter(bpy.types.Operator):
    bl_idname = "cut.line_to_cutter"
    bl_label = "Line to Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected_lines = [o for o in context.selected_objects if o.type == 'MESH']
        if not selected_lines: return {'CANCELLED'}
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
        props = context.scene.print_splitter_v08_props
        new_cutters = []
        for obj in selected_lines:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.edges.ensure_lookup_table()
            bm.verts.ensure_lookup_table()
            if not bm.edges: 
                bm.free()
                continue
            start_vert, ordered_pts, curr_vert, prev_edge = bm.verts[0], [], bm.verts[0], None
            while True:
                ordered_pts.append(obj.matrix_world @ curr_vert.co)
                next_edge = None
                for e in curr_vert.link_edges:
                    if e != prev_edge:
                        next_edge = e
                        break
                if not next_edge: break 
                curr_vert = next_edge.other_vert(curr_vert)
                if curr_vert == start_vert: break 
                prev_edge = next_edge
                if len(ordered_pts) > 100000: break
            M = len(ordered_pts)
            if M < 3: 
                bm.free()
                continue
            center = sum(ordered_pts, mathutils.Vector()) / M
            normal = mathutils.Vector()
            for i in range(M):
                v_curr, v_next = ordered_pts[i], ordered_pts[(i + 1) % M]
                normal.x += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
                normal.y += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
                normal.z += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)
            normal = mathutils.Vector((0, 0, 1)) if normal.length < 1e-6 else normal.normalized()
            matrix_world = mathutils.Matrix.LocRotScale(center, normal.to_track_quat('Z', 'Y'), None)
            matrix_inv = matrix_world.inverted()
            local_mid = [matrix_inv @ p for p in ordered_pts]
            min_dist = min(math.sqrt(p.x2 + p.y2) for p in local_mid)
            R_inner, outer_scale = min_dist * props.cutter_inner_scale, props.cutter_outer_scale
            outer_z_bu, inner_z_bu = get_bu(context, props.cutter_outer_z_offset), get_bu(context, props.cutter_inner_z_offset)
            local_inner, local_outer = [], []
            for p in local_mid:
                angle = math.atan2(p.y, p.x)
                local_inner.append(mathutils.Vector((R_inner * math.cos(angle), R_inner * math.sin(angle), inner_z_bu)))
                local_outer.append(mathutils.Vector((p.x * outer_scale, p.y * outer_scale, p.z + outer_z_bu)))
            center_pt = mathutils.Vector((0.0, 0.0, inner_z_bu))
            final_local_pts = local_inner + local_mid + local_outer + [center_pt]
            faces = []
            for i in range(M):
                next_i = (i + 1) % M
                faces.extend([[3*M, i, next_i], [i, M + i, M + next_i, next_i], [M + i, 2*M + i, 2*M + next_i, M + next_i]])
            mesh = bpy.data.meshes.new(obj.name.replace("Lines_", "") + "_Cutter_Mesh")
            mesh.from_pydata(final_local_pts, [], faces)
            mesh.update()
            cutter_obj = bpy.data.objects.new(obj.name.replace("Lines_", "") + "_Cutter", mesh)
            cutter_obj.matrix_world, cutter_obj.show_in_front, cutter_obj.display_type = matrix_world, True, 'WIRE'
            context.collection.objects.link(cutter_obj)
            
            cutter_obj.ez_cutter_inner_scale = props.cutter_inner_scale
            cutter_obj.ez_cutter_inner_z = props.cutter_inner_z_offset
            cutter_obj.ez_cutter_outer_scale = props.cutter_outer_scale
            cutter_obj.ez_cutter_outer_z = props.cutter_outer_z_offset
            cutter_obj.ez_cutter_thickness = props.cutter_thickness
            cutter_obj.ez_cutter_offset = props.cutter_offset

            solid_mod = cutter_obj.modifiers.new(name="Thickness", type='SOLIDIFY')
            solid_mod.thickness, solid_mod.offset = get_bu(context, props.cutter_thickness), float(props.cutter_offset)
            obj.hide_set(True) 
            guess_target = obj.name.split("Lines_")[-1].split(".")[0] if "Lines_" in obj.name else ""
            if not guess_target or guess_target not in bpy.data.objects: guess_target = props.target_mesh_name
            cutter_obj["target_mesh"] = guess_target 
            new_cutters.append(cutter_obj)
            bm.free()
        bpy.ops.object.select_all(action='DESELECT')
        for c in new_cutters:
            c.select_set(True)
            context.view_layer.objects.active = c
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class CUT_OT_flip_cutter(bpy.types.Operator):
    bl_idname = "cut.flip_cutter"
    bl_label = "Flip Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        cutters = [o for o in context.selected_objects if "_Cutter" in o.name and o.type == 'MESH']
        if not cutters: return {'CANCELLED'}
        for cutter in cutters: cutter.matrix_world = cutter.matrix_world @ mathutils.Matrix.Rotation(math.pi, 4, 'X')
        bpy.ops.ed.undo_push(message=T("Flip Cutter"))
        return {'FINISHED'}

def draw_callback_px(self, context):
    if getattr(self, "points", None) is None: return
    try: shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    except: shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    gpu.state.blend_set('ALPHA')
    gpu.state.point_size_set(12.0)
    gpu.state.line_width_set(3.0)
    if self.hover_point:
        batch_hover = batch_for_shader(shader, 'POINTS', {"pos": [self.hover_point]})
        shader.bind()
        shader.uniform_float("color", (0.2, 1.0, 0.2, 1.0))
        batch_hover.draw(shader)
    n = len(self.points)
    if n > 0:
        batch_pts = batch_for_shader(shader, 'POINTS', {"pos": self.points})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.2, 0.2, 1.0))
        batch_pts.draw(shader)
    lines = []
    if n > 0 and self.hover_point:
        for i in range(n - 1): lines.extend([self.points[i], self.points[i+1]])
        lines.extend([self.points[n-1], self.hover_point])
        if n >= 2: lines.extend([self.hover_point, self.points[0]])
    elif n > 0 and not self.hover_point:
        for i in range(n): lines.extend([self.points[i], self.points[(i+1)%n]])
    if lines:
        batch_lines = batch_for_shader(shader, 'LINES', {"pos": lines})
        shader.bind()
        shader.uniform_float("color", (1.0, 0.6, 0.1, 0.8))
        batch_lines.draw(shader)
    gpu.state.blend_set('NONE')

class CUT_OT_pick_three_points(bpy.types.Operator):
    bl_idname = "cut.pick_three_points"
    bl_label = "Multi-point Hand-drawn Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    def invoke(self, context, event):
        self.points, self.target_obj, self.hover_point = [], None, None
        try: context.window.cursor_modal_set('CROSSHAIR')
        except: pass
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(T("🖋️ [Hand-drawn Cutter] Left Click surface | MMB rotate | Right Click/ESC Generate"))
        return {'RUNNING_MODAL'}
    def cancel(self, context): 
        self.exit_modal(context) 
        context.area.header_text_set(None)
    def exit_modal(self, context):
        try: context.window.cursor_modal_restore()
        except: pass
        try: bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        except: pass
    def get_raycast(self, context, event):
        coord = event.mouse_region_x, event.mouse_region_y
        region, rv3d = context.region, context.region_data
        view_vector, ray_origin = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord), view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
        return context.scene.ray_cast(context.evaluated_depsgraph_get(), ray_origin, view_vector)
    def snap_to_mesh(self, obj, world_pt):
        succ, loc, _, _ = obj.closest_point_on_mesh(obj.matrix_world.inverted() @ world_pt)
        return obj.matrix_world @ loc if succ else world_pt
    def modal(self, context, event):
        context.area.tag_redraw() 
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'} or event.shift or event.ctrl or event.type.startswith('NUMPAD'): return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            if len(self.points) >= 3:
                self.hover_point = None
                self.create_cutter_mesh(context)
                self.exit_modal(context)
                bpy.ops.cut.adjust_cutter('INVOKE_DEFAULT')
                return {'FINISHED'}
            else:
                self.exit_modal(context)
                self.report({'WARNING'}, T("Points < 3, cancelled."))
                return {'CANCELLED'}
        if event.type == 'MOUSEMOVE':
            if event.alt: return {'PASS_THROUGH'}
            success, loc, _, _, hit_obj, _ = self.get_raycast(context, event)
            self.hover_point = loc if success and hit_obj.type == 'MESH' and (not self.target_obj or hit_obj == self.target_obj) else None
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hover_point:
                success, loc, _, _, hit_obj, _ = self.get_raycast(context, event)
                if not self.target_obj: self.target_obj = hit_obj
                if hit_obj == self.target_obj: self.points.append(self.hover_point)
        return {'RUNNING_MODAL'}
    def create_cutter_mesh(self, context):
        props = context.scene.print_splitter_v08_props
        N = len(self.points)
        snapped_points = [self.snap_to_mesh(self.target_obj, p) for p in self.points]
        snapped_mids = [self.snap_to_mesh(self.target_obj, (snapped_points[i] + snapped_points[(i+1)%N]) / 2.0) for i in range(N)]
        pts = []
        for i in range(N): pts.extend([snapped_points[i], snapped_mids[i]])
        M = 2 * N
        center = sum(pts, mathutils.Vector()) / M
        normal = mathutils.Vector()
        for i in range(M):
            v_curr, v_next = pts[i], pts[(i + 1) % M]
            normal.x += (v_curr.y - v_next.y) * (v_curr.z + v_next.z)
            normal.y += (v_curr.z - v_next.z) * (v_curr.x + v_next.x)
            normal.z += (v_curr.x - v_next.x) * (v_curr.y + v_next.y)
        normal = mathutils.Vector((0, 0, 1)) if normal.length < 1e-6 else normal.normalized()
        matrix_world = mathutils.Matrix.LocRotScale(center, normal.to_track_quat('Z', 'Y'), None)
        matrix_inv = matrix_world.inverted()
        local_mid = [matrix_inv @ p for p in pts]
        min_dist = min(math.sqrt(p.x2 + p.y2) for p in local_mid)
        R_inner, outer_scale = min_dist * props.cutter_inner_scale, props.cutter_outer_scale
        outer_z_bu, inner_z_bu = get_bu(context, props.cutter_outer_z_offset), get_bu(context, props.cutter_inner_z_offset)
        local_inner, local_outer = [], []
        for p in local_mid:
            angle = math.atan2(p.y, p.x)
            local_inner.append(mathutils.Vector((R_inner * math.cos(angle), R_inner * math.sin(angle), inner_z_bu)))
            local_outer.append(mathutils.Vector((p.x * outer_scale, p.y * outer_scale, p.z + outer_z_bu)))
        center_pt = mathutils.Vector((0.0, 0.0, inner_z_bu))
        final_local_pts = local_inner + local_mid + local_outer + [center_pt]
        faces = []
        for i in range(M):
            next_i = (i + 1) % M
            faces.extend([[3*M, i, next_i], [i, M + i, M + next_i, next_i], [M + i, 2*M + i, 2*M + next_i, M + next_i]])
        mesh = bpy.data.meshes.new("EZ_Cutter_Profile")
        mesh.from_pydata(final_local_pts, [], faces)
        mesh.update()
        cutter_obj = bpy.data.objects.new(self.target_obj.name + "_Cutter", mesh)
        cutter_obj.matrix_world, cutter_obj.show_in_front, cutter_obj.display_type = matrix_world, True, 'WIRE' 
        context.collection.objects.link(cutter_obj)
        
        cutter_obj.ez_cutter_inner_scale = props.cutter_inner_scale
        cutter_obj.ez_cutter_inner_z = props.cutter_inner_z_offset
        cutter_obj.ez_cutter_outer_scale = props.cutter_outer_scale
        cutter_obj.ez_cutter_outer_z = props.cutter_outer_z_offset
        cutter_obj.ez_cutter_thickness = props.cutter_thickness
        cutter_obj.ez_cutter_offset = props.cutter_offset

        solid_mod = cutter_obj.modifiers.new(name="Thickness", type='SOLIDIFY')
        solid_mod.thickness, solid_mod.offset = get_bu(context, props.cutter_thickness), float(props.cutter_offset)
        bpy.ops.object.select_all(action='DESELECT')
        cutter_obj.select_set(True)
        context.view_layer.objects.active = cutter_obj
        props.target_mesh_name = cutter_obj["target_mesh"] = self.target_obj.name
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

class CUT_OT_adjust_cutter(bpy.types.Operator):
    bl_idname = "cut.adjust_cutter"
    bl_label = "Adjust Cutter"
    bl_options = {'REGISTER', 'UNDO'}
    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'} or event.alt or event.shift or event.ctrl or event.type.startswith('NUMPAD'): return {'PASS_THROUGH'}
        context.area.header_text_set(T("🚀 Press G to move, SPACE/ENTER to Confirm!"))
        if event.type in {'SPACE', 'RET'} and event.value == 'PRESS':
            context.area.header_text_set(None)
            bpy.ops.object.mode_set(mode='OBJECT')
            for obj in context.selected_objects:
                if obj.type == 'MESH' and "_Cutter" in obj.name: 
                    rebuild_ez_cutter(context, obj, obj.ez_cutter_inner_scale, obj.ez_cutter_inner_z, obj.ez_cutter_outer_z, obj.ez_cutter_outer_scale)
            return {'FINISHED'}
        if event.type == 'ESC':
            context.area.header_text_set(None)
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'CANCELLED'}
        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class CUT_OT_execute(bpy.types.Operator):
    bl_idname = "cut.execute_cut"
    bl_label = "Execute Cut & Locate"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
        props = context.scene.print_splitter_v08_props
        
        selected_cutters = [o for o in context.selected_objects if "_Cutter" in o.name and o.type == 'MESH']
        if not selected_cutters: return {'CANCELLED'}
        
        manual_targets = [o for o in context.selected_objects if o.type == 'MESH' and "_Cutter" not in o.name and "_Peg" not in o.name and "_Locator" not in o.name]
        forced_target = manual_targets[0] if manual_targets else None

        target_groups = {}
        for cutter in selected_cutters:
            if forced_target:
                target_obj = forced_target
            else:
                target_name = cutter.get("target_mesh", "")
                if not target_name: target_name = cutter.name.split("_Cutter")[0].replace("Lines_", "")
                target_obj = bpy.data.objects.get(target_name)
                if not target_obj: target_obj = bpy.data.objects.get(props.target_mesh_name)
            
            if target_obj:
                if target_obj not in target_groups: target_groups[target_obj] = []
                target_groups[target_obj].append(cutter)
                
        if not target_groups: return {'CANCELLED'}
        
        all_final_objs = []
        try:
            for target_obj, cutters in target_groups.items():
                locators_distribute = [] 
                for cutter_obj in cutters:
                    mod_name = "Thickness" if "Thickness" in cutter_obj.modifiers else ("切割厚度" if "切割厚度" in cutter_obj.modifiers else None)
                    if mod_name:
                        cutter_obj.modifiers[mod_name].thickness, cutter_obj.modifiers[mod_name].offset = get_bu(context, cutter_obj.ez_cutter_thickness), float(cutter_obj.ez_cutter_offset)
                    bpy.ops.object.select_all(action='DESELECT')
                    cutter_obj.select_set(True)
                    context.view_layer.objects.active = cutter_obj
                    if mod_name: apply_modifier_safely(cutter_obj, mod_name)
                    loc_world = cutter_obj.matrix_world @ cutter_obj.data.vertices[-1].co if len(cutter_obj.data.vertices) > 0 else cutter_obj.location
                    clean_matrix = mathutils.Matrix.LocRotScale(loc_world, cutter_obj.matrix_world.to_quaternion(), (1.0, 1.0, 1.0))
                    loc_obj = bpy.data.objects.new(cutter_obj.name.replace("_Cutter", "_Locator"), None)
                    loc_obj.empty_display_type, loc_obj.empty_display_size, loc_obj.matrix_world = 'ARROWS', max(target_obj.dimensions) * 0.1, clean_matrix
                    context.collection.objects.link(loc_obj)
                    locators_distribute.append(loc_obj)
                    bpy.ops.object.select_all(action='DESELECT')
                    target_obj.select_set(True)
                    context.view_layer.objects.active = target_obj
                    bool_mod = target_obj.modifiers.new(name=f"EZ_Bool_{cutter_obj.name}", type='BOOLEAN')
                    bool_mod.operation, bool_mod.object = 'DIFFERENCE', cutter_obj
                    bool_mod.solver = 'EXACT' if props.use_exact_bool else 'FAST'
                    apply_modifier_safely(target_obj, bool_mod.name) 
                    safe_remove_object(cutter_obj)
                bpy.ops.object.select_all(action='DESELECT')
                target_obj.select_set(True)
                context.view_layer.objects.active = target_obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.mode_set(mode='OBJECT')
                separated_objs = [o for o in context.selected_objects if o and o.type == 'MESH']
                separated_objs.sort(key=lambda o: sum(o.dimensions), reverse=True)
                if len(separated_objs) < 2: continue
                main_body = separated_objs[0]
                intended_parts = set()
                for loc_obj in locators_distribute:
                    best_obj, min_dist = None, float('inf')
                    for obj in separated_objs[1:]:
                        succ, pt, _, _ = obj.closest_point_on_mesh(obj.matrix_world.inverted() @ loc_obj.location)
                        if succ:
                            dist = (obj.matrix_world @ pt - loc_obj.location).length
                            if dist < min_dist: min_dist, best_obj = dist, obj
                    if best_obj: intended_parts.add(best_obj)
                accidental_parts = [o for o in separated_objs if o != main_body and o not in intended_parts]
                if accidental_parts:
                    bpy.ops.object.select_all(action='DESELECT')
                    for o in accidental_parts: o.select_set(True)
                    main_body.select_set(True)
                    context.view_layer.objects.active = main_body
                    bpy.ops.object.join()
                final_sorted = [main_body] + list(intended_parts)
                final_sorted.sort(key=lambda o: sum(o.dimensions), reverse=True)
                all_final_objs.extend(final_sorted)
                
                props.peg_females.clear()
                if len(final_sorted) > 0: props.peg_male_obj = final_sorted[0]
                for obj in final_sorted[1:]:
                    item = props.peg_females.add()
                    item.obj = obj
                move_to_collection(final_sorted, f"{target_obj.name}{T('_Assembly_Result')}", context)
                
            if all_final_objs: self.report({'INFO'}, T("Batch cut and locate successful!"))
        except Exception as e: return {'CANCELLED'}
        finally: bpy.ops.ed.undo_push(message=T("Apply Cutter"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_convert_to_custom_peg(bpy.types.Operator):
    bl_idname = "printprep_v08.convert_to_custom_peg"
    bl_label = "Convert to Smart Peg"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.type == 'MESH']
        if not selected_objs: 
            self.report({'WARNING'}, T("Please select a mesh object first to convert!"))
            return {'CANCELLED'}
        
        props = context.scene.print_splitter_v08_props
        for obj in selected_objs:
            if "_Peg_Preview" not in obj.name:
                obj.name = f"{obj.name}_Peg_Preview"
            obj["is_custom_peg"] = True
            obj.ez_peg_tolerance = props.ez_peg_tolerance
            obj.display_type = 'WIRE'
            obj.show_in_front = True
            
        self.report({'INFO'}, T("Converted {} objects to custom pegs!").format(len(selected_objs)))
        return {'FINISHED'}

class PRINTPREP_V08_OT_interactive_add_peg(bpy.types.Operator):
    bl_idname = "printprep_v08.interactive_add_peg"
    bl_label = "Add Peg on Surface"
    bl_options = {'REGISTER', 'UNDO'}
    def invoke(self, context, event):
        if context.active_object is None or context.active_object.type != 'MESH': return {'CANCELLED'}
        self.target_obj = context.active_object
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set(T("🔨 Click surface to locate peg | MMB rotate | RClick/ESC exit"))
        return {'RUNNING_MODAL'}
    def cancel(self, context): context.area.header_text_set(None)
    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'TRACKPADPAN', 'TRACKPADZOOM'} or event.alt or event.shift or event.ctrl or event.type.startswith('NUMPAD'): return {'PASS_THROUGH'}
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.header_text_set(None)
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            coord = event.mouse_region_x, event.mouse_region_y
            region, rv3d = context.region, context.region_data
            view_vector, ray_origin = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord), view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            matrix_inv = self.target_obj.matrix_world.inverted()
            success, loc, normal, poly_index = self.target_obj.ray_cast(matrix_inv @ ray_origin, matrix_inv @ (ray_origin + view_vector * 10000) - matrix_inv @ ray_origin)
            if success:
                world_loc = self.target_obj.matrix_world @ loc
                world_normal = (self.target_obj.matrix_world.to_3x3() @ normal).normalized()
                loc_obj = bpy.data.objects.new(self.target_obj.name + "_Locator", None)
                loc_obj.empty_display_type, loc_obj.empty_display_size = 'ARROWS', 5.0
                loc_obj.matrix_world = mathutils.Matrix.LocRotScale(world_loc, world_normal.to_track_quat('Z', 'Y'), (1, 1, 1))
                context.collection.objects.link(loc_obj)
                bpy.ops.object.select_all(action='DESELECT')
                loc_obj.select_set(True)
                context.view_layer.objects.active = loc_obj
                bpy.ops.cut.batch_generate_peg_preview('EXEC_DEFAULT')
                bpy.ops.object.select_all(action='DESELECT')
                self.target_obj.select_set(True)
                context.view_layer.objects.active = self.target_obj
        return {'PASS_THROUGH'}

class CUT_OT_flip_locator(bpy.types.Operator):
    bl_idname = "cut.flip_locator"
    bl_label = "Flip Locator"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        processed = set()
        for obj in context.selected_objects:
            loc, peg = None, None
            if "_Locator" in obj.name:
                loc = obj
                if obj.name.replace("_Locator", "_Peg_Preview") in bpy.data.objects: peg = bpy.data.objects[obj.name.replace("_Locator", "_Peg_Preview")]
            elif "_Peg_Preview" in obj.name:
                peg = obj
                if obj.name.replace("_Peg_Preview", "_Locator") in bpy.data.objects: loc = bpy.data.objects[obj.name.replace("_Peg_Preview", "_Locator")]
            if loc and loc.name not in processed:
                loc.matrix_world = loc.matrix_world @ mathutils.Matrix.Rotation(math.pi, 4, 'X')
                processed.add(loc.name)
                if peg: peg.matrix_world = loc.matrix_world
        return {'FINISHED'}

class CUT_OT_batch_generate_peg_preview(bpy.types.Operator):
    bl_idname = "cut.batch_generate_peg_preview"
    bl_label = "Generate Preview"
    bl_options = {'REGISTER', 'UNDO'}
    def get_obj_center(self, obj): return obj.matrix_world @ (sum((mathutils.Vector(b) for b in obj.bound_box), mathutils.Vector()) / 8.0)
    def execute(self, context):
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
        locators = [o for o in context.selected_objects if "_Locator" in o.name and o.type != 'MESH']
        if not locators: return {'CANCELLED'}
        props = context.scene.print_splitter_v08_props
        male_obj = props.peg_male_obj
        valid_females = [item.obj for item in props.peg_females if item.obj]
        L, r_base, r_top, segs = props.ez_peg_length, props.ez_peg_dia_base / 2.0, props.ez_peg_dia_top / 2.0, props.ez_peg_segments
        for locator in locators:
            bpy.ops.object.select_all(action='DESELECT')
            old_peg_name = locator.name.replace("_Locator", "_Peg_Preview")
            if old_peg_name in bpy.data.objects: safe_remove_object(bpy.data.objects[old_peg_name])
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=get_bu(context, r_base), radius2=get_bu(context, r_top), depth=get_bu(context, L))
            mesh = bpy.data.meshes.new("EZ_Peg_Preview_Mesh")
            bm.to_mesh(mesh)
            bm.free()
            peg = bpy.data.objects.new(old_peg_name, mesh)
            context.collection.objects.link(peg)
            context.view_layer.objects.active = peg
            peg.show_in_front, peg.display_type = True, 'WIRE'
            
            peg.ez_peg_segments = props.ez_peg_segments
            peg.ez_peg_dia_base = props.ez_peg_dia_base
            peg.ez_peg_dia_top = props.ez_peg_dia_top
            peg.ez_peg_length = props.ez_peg_length
            peg.ez_peg_chamfer = props.ez_peg_chamfer
            peg.ez_peg_tolerance = props.ez_peg_tolerance

            if male_obj and valid_females:
                loc_z = (locator.matrix_world.to_3x3() @ mathutils.Vector((0, 0, 1))).normalized()
                closest_fem = min(valid_females, key=lambda f: (self.get_obj_center(f) - locator.location).length)
                if loc_z.dot((self.get_obj_center(closest_fem) - locator.location).normalized()) < 0:
                    locator.matrix_world = locator.matrix_world @ mathutils.Matrix.Rotation(math.pi, 4, 'X')
            peg.matrix_world = locator.matrix_world
            if props.ez_peg_chamfer > 0:
                bevel = peg.modifiers.new("Chamfer", 'BEVEL')
                bevel.width, bevel.segments, bevel.limit_method, bevel.angle_limit = get_bu(context, props.ez_peg_chamfer), 1, 'ANGLE', 0.785398
            bpy.ops.object.shade_smooth()
        for obj in locators: obj.select_set(True)
        if locators: context.view_layer.objects.active = locators[0]
        return {'FINISHED'}

class CUT_OT_batch_assemble(bpy.types.Operator):
    bl_idname = "cut.batch_assemble"
    bl_label = "Execute Physical Assembly"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if context.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
        peg_previews = [o for o in bpy.data.objects if "_Peg_Preview" in o.name and o.type == 'MESH']
        if not peg_previews: return {'CANCELLED'}
        props = context.scene.print_splitter_v08_props
        male_obj = props.peg_male_obj
        females = [item.obj for item in props.peg_females if item.obj]
        if not male_obj and not females: return {'CANCELLED'}
        solver_type = 'EXACT' if props.use_exact_bool else 'FAST'
        try:
            hole_tools = []
            for peg in peg_previews:
                hole = peg.copy()
                hole.data = peg.data.copy()
                context.collection.objects.link(hole)
                peg_tol = peg.ez_peg_tolerance if hasattr(peg, "ez_peg_tolerance") else props.ez_peg_tolerance
                if peg_tol > 0:
                    disp = hole.modifiers.new("EZ_Tol", 'DISPLACE')
                    disp.mid_level, disp.strength = 0.0, get_bu(context, peg_tol)
                hole.display_type = 'WIRE'
                hole_tools.append(hole)
            for female in females:
                for hole in hole_tools:
                    bpy.ops.object.select_all(action='DESELECT')
                    female.select_set(True)
                    context.view_layer.objects.active = female
                    mod_f = female.modifiers.new(name="EZ_Female_Hole", type='BOOLEAN')
                    mod_f.operation, mod_f.object, mod_f.solver = 'DIFFERENCE', hole, solver_type
                    apply_modifier_safely(female, mod_f.name)
            if male_obj:
                mode = props.peg_assembly_mode
                if mode == 'FUSE':
                    for peg in peg_previews:
                        bpy.ops.object.select_all(action='DESELECT')
                        male_obj.select_set(True)
                        context.view_layer.objects.active = male_obj
                        mod_m = male_obj.modifiers.new(name="EZ_Male_Add", type='BOOLEAN')
                        mod_m.operation, mod_m.object, mod_m.solver = 'UNION', peg, solver_type
                        apply_modifier_safely(male_obj, mod_m.name)
                        safe_remove_object(peg)
                elif mode == 'INDEPENDENT':
                    for hole in hole_tools:
                        bpy.ops.object.select_all(action='DESELECT')
                        male_obj.select_set(True)
                        context.view_layer.objects.active = male_obj
                        mod_m = male_obj.modifiers.new(name="EZ_Male_Hole", type='BOOLEAN')
                        mod_m.operation, mod_m.object, mod_m.solver = 'DIFFERENCE', hole, solver_type
                        apply_modifier_safely(male_obj, mod_m.name)
                    for idx, peg in enumerate(peg_previews):
                        peg.name, peg.display_type, peg.show_in_front = f"{male_obj.name}_Final_Peg_{idx+1:02d}", 'TEXTURED', False
            for hole in hole_tools: safe_remove_object(hole)
            for o in bpy.data.objects:
                if "_Locator" in o.name and o.type == 'EMPTY': bpy.data.objects.remove(o, do_unlink=True)
            props.peg_male_obj = None
            props.peg_females.clear()
            self.report({'INFO'}, T("Batch assembly executed!"))
        except Exception as e: return {'CANCELLED'}
        finally: bpy.ops.ed.undo_push(message=T("Execute Physical Assembly"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_smooth_lines(bpy.types.Operator):
    bl_idname = "printprep_v08.smooth_lines"
    bl_label = "Smooth Lines"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.print_splitter_v08_props
        objs = context.selected_objects[:]
        if context.mode == 'EDIT_MESH': bpy.ops.object.mode_set(mode='OBJECT')
        for obj in objs:
            if obj.type != 'MESH': continue
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            if props.smooth_iterations > 0: bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=props.smooth_iterations)
            if props.line_decimate_ratio < 1.0:
                bm = bmesh.from_edit_mesh(obj.data)
                verts = [v for v in bm.verts if v.select]
                if len(verts) > 6:
                    remove_count = len(verts) - max(4, int(len(verts) * props.line_decimate_ratio))
                    if remove_count > 0:
                        step = len(verts) / float(remove_count)
                        bmesh.ops.dissolve_verts(bm, verts=[verts[int(i * step)] for i in range(remove_count) if int(i * step) < len(verts)])
                bmesh.update_edit_mesh(obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
        for obj in objs: obj.select_set(True)
        bpy.ops.ed.undo_push(message=T("Undo: Smooth Lines"))
        return {'FINISHED'}

class PRINTPREP_V08_OT_standalone_fill_holes(bpy.types.Operator):
    bl_idname = "printprep_v08.standalone_fill_holes"
    bl_label = "Smart Cap Holes"
    bl_options = {'REGISTER', 'UNDO'}
    fill_method: bpy.props.StringProperty(default='FLAT')
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'MESH': 
                context.view_layer.objects.active = obj
                perform_capping(obj, self.fill_method)
        return {'FINISHED'}

class PRINTPREP_V08_OT_extrude_and_flatten(bpy.types.Operator):
    bl_idname = "printprep_v08.extrude_and_flatten"
    bl_label = "Extrude & Flatten"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if context.mode != 'EDIT_MESH': return {'CANCELLED'}
        dist = get_bu(context, context.scene.print_splitter_v08_props.ez_peg_length)
        for obj in context.objects_in_edit_mode:
            try: bpy.ops.mesh.edge_face_add()
            except: pass
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, dist)})
        bpy.ops.transform.resize(value=(1, 1, 0), constraint_axis=(False, False, True))
        return {'FINISHED'}

class PRINTPREP_V08_OT_safe_flange_extrude(bpy.types.Operator):
    bl_idname = "printprep_v08.safe_flange_extrude"
    bl_label = "Safe Flange Extrude"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if context.mode != 'EDIT_MESH': return {'CANCELLED'}
        for obj in context.objects_in_edit_mode:
            bm = bmesh.from_edit_mesh(obj.data)
            sel_verts, sel_edges = [v for v in bm.verts if v.select], [e for e in bm.edges if e.select]
            if not sel_edges: continue
            C_world = obj.matrix_world @ (sum((v.co for v in sel_verts), mathutils.Vector()) / len(sel_verts))
            safe_rad = get_bu(context, 10.0) 
            new_verts = [e for e in bmesh.ops.extrude_edge_only(bm, edges=sel_edges)['geom'] if isinstance(e, bmesh.types.BMVert)]
            matrix_inv = obj.matrix_world.inverted()
            for nv in new_verts:
                old_v = next((e.other_vert(nv) for e in nv.link_edges if e.other_vert(nv) in sel_verts), None)
                if old_v:
                    ov_world = obj.matrix_world @ old_v.co
                    vec = ov_world - C_world
                    if context.scene.print_splitter_v08_props.flange_mode == 'XY': vec.z = 0
                    if vec.length < 0.0001: vec = mathutils.Vector((1,0,0))
                    new_pos = C_world + vec.normalized() * safe_rad
                    if context.scene.print_splitter_v08_props.flange_mode == 'XY': new_pos.z = ov_world.z
                    nv.co = matrix_inv @ new_pos
            for v in bm.verts: v.select = False
            for nv in new_verts: nv.select = True
            bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}

class PRINTPREP_V08_OT_boolean_hollow(bpy.types.Operator):
    bl_idname = "printprep_v08.boolean_hollow"
    bl_label = "Boolean Hollow"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        props = context.scene.print_splitter_v08_props
        thickness = get_bu(context, props.hollow_thickness)
        selected = [o for o in context.selected_objects if o.type == 'MESH']
        if not selected: return {'CANCELLED'}
        for obj in selected:
            if obj.data.users > 1: obj.data = obj.data.copy()
            core = obj.copy()
            core.data = obj.data.copy()
            core.name = f"{obj.name}_Hollow_Core"
            context.collection.objects.link(core)
            core.parent, core.matrix_parent_inverse, core.display_type, core.hide_render = obj, obj.matrix_world.inverted(), 'BOUNDS', True
            disp = core.modifiers.new(name="Hollow_Shrink", type='DISPLACE')
            disp.mid_level, disp.strength = 0.0, -thickness
            bool_mod = obj.modifiers.new(name="FDM_Hollow_Bool", type='BOOLEAN')
            bool_mod.operation, bool_mod.object = 'DIFFERENCE', core
            apply_modifier_safely(obj, bool_mod.name)
        return {'FINISHED'}

class PRINTPREP_V08_OT_drop_to_floor(bpy.types.Operator):
    bl_idname = "printprep_v08.drop_to_floor"
    bl_label = "Drop to Floor"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        selected_objs = [o for o in context.selected_objects if o.type == 'MESH']
        for obj in selected_objs:
            if len(obj.data.vertices) < 4: continue
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            if obj.data.users > 1: obj.data = obj.data.copy()
            z_coords = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
            if z_coords:
                obj.matrix_world.translation.z -= min(z_coords)
                try: bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                except Exception as e: pass
        for obj in selected_objs: obj.select_set(True)
        if selected_objs: context.view_layer.objects.active = selected_objs[0]
        return {'FINISHED'}

# ================= UI Panel (暴力强制注入翻译版) =================
class PRINTPREP_V08_PT_panel(bpy.types.Panel):
    bl_label = "Little Prince 3D Part Splitter"
    bl_idname = "PRINTPREP_V08_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "PrintPrep"

    def draw(self, context):
        layout = self.layout
        props = context.scene.print_splitter_v08_props
        
        box = layout.box()
        box.label(text=T("1. Base Size & Position"), icon='CON_SIZELIKE')
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("printprep_v08.setup_units", text=T("Set Metric (mm)"), icon='WORLD_DATA')
        row.operator("printprep_v08.measure_tool", text=T("Measure Tool Snap"), icon='VIEW_ZOOM')
        row = col.row(align=True)
        row.prop(props, "target_dimension", text=T("Target Size (mm)"))
        row.prop(props, "is_uniform", text=T("Uniform Scale"), toggle=True)
        row = col.row(align=True)
        row.prop(props, "scale_axis", text="")
        row.operator("printprep_v08.absolute_scale", text=T("Absolute Scale"), icon='OBJECT_DATAMODE')
        row.operator("printprep_v08.drop_to_floor", text=T("Drop to Floor"), icon='TRIA_DOWN')

        box = layout.box()
        box.label(text=T("2. Topology & Face Sets"), icon='BRUSH_DATA')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props, "clean_merge_distance", text=T("Merge Threshold"))
        row.operator("cut.clean_mesh", text=T("Clean Debris"), icon='BRUSH_DATA')
        row = col.row(align=True)
        row.prop(props, "decimate_ratio", text=T("Decimate Ratio"))
        row.operator("printprep_v08.decimate_mesh", text=T("Decimate Mesh"), icon='MOD_DECIM')
        box.separator()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props, "recalc_threshold", text=T("Recalc Threshold"))
        row.operator("printprep_v08.recalc_face_sets", text=T("Regenerate Face Sets"), icon='FILE_REFRESH')
        col.operator("printprep_v08.enter_brush_mode", text=T("Native Brush Mode"), icon='SCULPTMODE_HLT')
        box.separator()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props, "top_n_count", text=T("Keep Top N"))
        row.operator("printprep_v08.keep_top_n", text=T("Keep Large Parts"), icon='FILTER')
        row = col.row(align=True)
        row.prop(props, "min_face_count", text=T("Island Threshold"))
        row.operator("printprep_v08.clean_by_threshold", text=T("Clean Small Islands"), icon='BRUSH_DATA')
        col.operator("printprep_v08.interactive_merge", text=T("Interactive Merge (Tool)"), icon='EYEDROPPER')

        box = layout.box()
        box.label(text=T("3. Non-destructive Splitting"), icon='MOD_EXPLODE')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props, "auto_cap", text=T("Auto Cap"), toggle=True)
        row.prop(props, "keep_boundary", text=T("Extract Boundaries"), toggle=True)
        if props.auto_cap: col.prop(props, "cap_method", text=T("Cap Method"))
        if props.keep_boundary: col.prop(props, "line_output_mode", text=T("Line Output"))
        col = box.column(align=True)
        op_all = col.operator("printprep_v08.split_face_sets", text=T("Split Face Sets"), icon='AUTO')
        op_all.split_mode = 'ALL'
        col.operator("printprep_v08.interactive_split", text=T("Interactive Peel (Tool)"), icon='RESTRICT_SELECT_OFF')
        col.operator("printprep_v08.extract_boundaries_only", text=T("Extract Pure Boundaries"), icon='OUTLINER_OB_CURVE')

        box = layout.box()
        box.label(text=T("4. Smart Cutter"), icon='EVENT_M')
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("cut.line_to_cutter", text=T("Line to Cutter"), icon='CON_FOLLOWPATH')
        row.operator("cut.flip_cutter", text=T("Flip"), icon='UV_SYNC_SELECT')
        col.operator("cut.pick_three_points", text=T("Multi-point Hand-drawn Cutter"), icon='LINE_DATA')
        box.separator()
        
        active_obj = context.active_object
        valid_cutter = active_obj and "_Cutter" in active_obj.name and active_obj.type == 'MESH'
        source = active_obj if valid_cutter else props
        
        if source == props:
            inner_s, inner_z = "cutter_inner_scale", "cutter_inner_z_offset"
            outer_s, outer_z = "cutter_outer_scale", "cutter_outer_z_offset"
            thick, offset = "cutter_thickness", "cutter_offset"
        else:
            inner_s, inner_z = "ez_cutter_inner_scale", "ez_cutter_inner_z"
            outer_s, outer_z = "ez_cutter_outer_scale", "ez_cutter_outer_z"
            thick, offset = "ez_cutter_thickness", "ez_cutter_offset"

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(source, inner_s, text=T("Inner Scale"))
        row.prop(source, inner_z, text=T("Inner Z Offset"))
        row = col.row(align=True)
        row.prop(source, outer_s, text=T("Outer Scale"))
        row.prop(source, outer_z, text=T("Outer Z Offset"))
        row = col.row(align=True)
        row.prop(source, thick, text=T("Thickness"))
        row.prop(source, offset, text=T("Offset Dir"))
        
        col = box.column(align=True)
        col.prop(props, "use_exact_bool", text=T("Exact Boolean (Safe)"))
        col.operator("cut.execute_cut", text=T("Execute Cut & Locate"), icon='MOD_BOOLEAN')

        box = layout.box()
        box.label(text=T("5. Smart Assembly Pegs"), icon='MOD_BUILD')
        
        valid_peg = active_obj and ("_Peg_Preview" in active_obj.name or "_Locator" in active_obj.name)
        peg_obj = None
        is_custom_peg = False
        
        if valid_peg:
            if "_Locator" in active_obj.name:
                peg_obj = bpy.data.objects.get(active_obj.name.replace("_Locator", "_Peg_Preview"))
            else:
                peg_obj = active_obj
            if peg_obj and peg_obj.get("is_custom_peg"):
                is_custom_peg = True

        source = peg_obj if peg_obj else props
        s_segs, s_tol, s_base, s_top, s_len, s_cham = "ez_peg_segments", "ez_peg_tolerance", "ez_peg_dia_base", "ez_peg_dia_top", "ez_peg_length", "ez_peg_chamfer"

        col = box.column(align=True)
        if not is_custom_peg:
            row = col.row(align=True)
            row.prop(source, s_segs, text=T("Segments (Anti-twist)"))
            row.prop(source, s_tol, text=T("Tolerance"))
            row = col.row(align=True)
            row.prop(source, s_base, text=T("Base Dia (Male)"))
            row.prop(source, s_top, text=T("Top Dia (Female)"))
            row = col.row(align=True)
            row.prop(source, s_len, text=T("Total Length"))
            row.prop(source, s_cham, text=T("Chamfer"))
        else:
            col.label(text=T("✨ Custom Peg Active"), icon='OUTLINER_OB_MESH')
            col.prop(source, s_tol, text=T("Peg Tolerance (Only Active)"))
            
        col = box.column(align=True)
        col.scale_y = 1.2
        row_op = col.row(align=True)
        row_op.operator("printprep_v08.interactive_add_peg", text=T("Click Surface to Add Peg"), icon='MESH_CONE')
        row_op.operator("printprep_v08.convert_to_custom_peg", text=T("Convert to Smart Peg"), icon='TRANSFORM_ORIGINS')
        
        row = col.row(align=True)
        row.operator("cut.batch_generate_peg_preview", text=T("Generate Preview"), icon='FILE_REFRESH')
        row.operator("cut.flip_locator", text=T("Flip Locator"), icon='UV_SYNC_SELECT')
        
        row_toggle = box.row()
        
        # ========== [完美修复的 Assembly List] ==========
        label_text = T("Assembly List (Total {} Parts)").format(len(props.peg_females))
        row_toggle.prop(props, "show_peg_list", icon="TRIA_DOWN" if props.show_peg_list else "TRIA_RIGHT", text=label_text, emboss=False)
        if props.show_peg_list:
            box_obj = box.box()
            box_obj.prop(props, "peg_male_obj", text=T("Male Part (Main)"))
            if len(props.peg_females) == 0: box_obj.label(text=T("Auto loading parts after cut..."), icon='INFO')
            for i, item in enumerate(props.peg_females): 
                box_obj.prop(item, "obj", text=T("Female Part {}").format(i+1))
        col = box.column(align=True)
        col.prop(props, "peg_assembly_mode", text="")
        col.operator("cut.batch_assemble", text=T("Execute Physical Assembly"), icon='MOD_BOOLEAN')

        box = layout.box()
        box.label(text=T("6. Boundary & Shell"), icon='TOOL_SETTINGS')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(props, "smooth_iterations", text=T("Smooth Iterations"))
        row.prop(props, "line_decimate_ratio", text=T("Keep Ratio"))
        col.operator("printprep_v08.smooth_lines", text=T("Smooth Lines"), icon='MOD_SMOOTH')
        box.separator()
        col = box.column(align=True)
        row = col.row(align=True)
        op1 = row.operator("printprep_v08.standalone_fill_holes", text=T("Cap (Flat)"), icon='MESH_PLANE')
        op1.fill_method = 'FLAT'
        op2 = row.operator("printprep_v08.standalone_fill_holes", text=T("Cap (Curved)"), icon='MESH_ICOSPHERE')
        op2.fill_method = 'CURVED'
        row = col.row(align=True)
        row.operator("printprep_v08.extrude_and_flatten", text=T("Extrude & Flatten"), icon='CON_TRANSLIKE')
        row.prop(props, "flange_mode", text="")
        row.operator("printprep_v08.safe_flange_extrude", text=T("Safe Flange Extrude"), icon='MOD_THICKNESS')
        row = col.row(align=True)
        row.prop(props, "hollow_thickness", text=T("Hollow Thickness"))
        row.operator("printprep_v08.boolean_hollow", text=T("Boolean Hollow"), icon='MOD_SOLIDIFY')

classes = (
    ObjectPointerItem,
    PrintSplitterV08Properties,
    PRINTPREP_V08_OT_setup_units,
    PRINTPREP_V08_OT_measure_tool,
    PRINTPREP_V08_OT_absolute_scale,
    CUT_OT_clean_mesh,
    PRINTPREP_V08_OT_decimate_mesh,
    PRINTPREP_V08_OT_recalc_face_sets,
    PRINTPREP_V08_OT_enter_brush_mode,
    PRINTPREP_V08_OT_keep_top_n,
    PRINTPREP_V08_OT_clean_by_threshold,
    PRINTPREP_V08_OT_interactive_merge,
    PRINTPREP_V08_OT_interactive_split,
    PRINTPREP_V08_OT_split_face_sets,
    PRINTPREP_V08_OT_extract_boundaries_only,
    CUT_OT_line_to_cutter,
    CUT_OT_flip_cutter,
    CUT_OT_pick_three_points,
    CUT_OT_adjust_cutter,
    CUT_OT_execute,
    PRINTPREP_V08_OT_convert_to_custom_peg,
    PRINTPREP_V08_OT_interactive_add_peg,
    CUT_OT_flip_locator,
    CUT_OT_batch_generate_peg_preview,
    CUT_OT_batch_assemble,
    PRINTPREP_V08_OT_smooth_lines,
    PRINTPREP_V08_OT_standalone_fill_holes,
    PRINTPREP_V08_OT_extrude_and_flatten,
    PRINTPREP_V08_OT_safe_flange_extrude,
    PRINTPREP_V08_OT_boolean_hollow,
    PRINTPREP_V08_OT_drop_to_floor,
    PRINTPREP_V08_PT_panel,
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.print_splitter_v08_props = bpy.props.PointerProperty(type=PrintSplitterV08Properties)
    
    # 清理可能存在的旧字典，防止报错
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
        
    # 注册双语字典
    bpy.app.translations.register(__name__, translations_dict)
    
    bpy.types.Object.ez_cutter_inner_scale = bpy.props.FloatProperty(name="Inner Scale", default=0.85, min=0.01, max=2.0, update=update_single_cutter_geo)
    bpy.types.Object.ez_cutter_inner_z = bpy.props.FloatProperty(name="Inner Z Offset", default=0.0, min=-50.0, max=50.0, update=update_single_cutter_geo)
    bpy.types.Object.ez_cutter_outer_scale = bpy.props.FloatProperty(name="Outer Scale", default=1.3, min=1.01, max=10.0, update=update_single_cutter_geo)
    bpy.types.Object.ez_cutter_outer_z = bpy.props.FloatProperty(name="Outer Z Offset", default=0.0, min=-50.0, max=50.0, update=update_single_cutter_geo)
    bpy.types.Object.ez_cutter_thickness = bpy.props.FloatProperty(name="Thickness", default=0.5, min=0.01, max=500.0, update=update_single_cutter_mod)
    bpy.types.Object.ez_cutter_offset = bpy.props.EnumProperty(name="Offset Dir", items=[('0', "Center", ""), ('1', "Outward", ""), ('-1', "Inward", "")], default='0', update=update_single_cutter_mod)

    bpy.types.Object.ez_peg_segments = bpy.props.IntProperty(name="Segments (Anti-twist)", default=6, min=3, max=64, update=update_single_peg)
    bpy.types.Object.ez_peg_dia_base = bpy.props.FloatProperty(name="Base Dia (Male)", default=10.0, min=0.1, max=500.0, update=update_single_peg)
    bpy.types.Object.ez_peg_dia_top = bpy.props.FloatProperty(name="Top Dia (Female)", default=8.0, min=0.1, max=500.0, update=update_single_peg)
    bpy.types.Object.ez_peg_length = bpy.props.FloatProperty(name="Total Length", default=20.0, min=1.0, max=1000.0, update=update_single_peg)
    bpy.types.Object.ez_peg_chamfer = bpy.props.FloatProperty(name="Chamfer", default=0.6, min=0.0, max=5.0, update=update_single_peg)
    bpy.types.Object.ez_peg_tolerance = bpy.props.FloatProperty(name="Tolerance", default=0.2, min=0.0, max=5.0, step=0.05, update=update_single_peg)

def unregister():
    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass
        
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.Scene.print_splitter_v08_props
    
    del bpy.types.Object.ez_cutter_inner_scale
    del bpy.types.Object.ez_cutter_inner_z
    del bpy.types.Object.ez_cutter_outer_scale
    del bpy.types.Object.ez_cutter_outer_z
    del bpy.types.Object.ez_cutter_thickness
    del bpy.types.Object.ez_cutter_offset
    del bpy.types.Object.ez_peg_segments
    del bpy.types.Object.ez_peg_dia_base
    del bpy.types.Object.ez_peg_dia_top
    del bpy.types.Object.ez_peg_length
    del bpy.types.Object.ez_peg_chamfer
    del bpy.types.Object.ez_peg_tolerance

if __name__ == "__main__": 
    register()