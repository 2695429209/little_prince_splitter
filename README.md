# little_prince_splitter
blender 插件
小王子 3D拆件工作站 (Little Prince 3D Part Splitter)
小王子 3D拆件工作站 是一款专为 FDM/SLA 3D 打印玩家和手办模型师打造的 Blender 高效分件插件。它能将复杂的模型拆分、打孔、生成防呆插销和布尔运算等繁琐步骤，简化为顺滑的“点选”交互体验。

无论你是要将大型模型拆分成适合打印机尺寸的小块，还是为手办制作高精度的拼装插销，这款插件都能为你节省大量时间！

Little Prince 3D Part Splitter is a powerful, highly interactive Blender add-on designed for 3D printing enthusiasts and figure sculptors. It simplifies the tedious process of mesh splitting, boolean cutting, and generating precision assembly pegs into a seamless, click-and-drag workflow.

🌟 核心功能 (Core Features)
1. 📏 精确的物理尺寸控制 (Precision Sizing & Prep)
一键环境转毫米：自动将 Blender 的场景单位和裁剪视图切换为 3D 打印标准的毫米 (mm)。

绝对缩放 (Absolute Scale)：输入你想要的物理尺寸，自动等比/非等比缩放整个模型。

一键贴地 (Drop to Floor)：让模型的最低点瞬间贴齐世界坐标零点。

2. 🎨 面组级无损拆件 (Interactive Face Set Splitting)
智能面组规划：基于曲率和连通性，自动为模型生成多彩面组。

交互式射吸融合：像吸管一样吸取颜色，左键点击即可融合零碎的面组。

透视剥离 (Interactive Peel)：隔着屏幕点选想要的色块，一键将它们单独剥离成新物体，并支持自动封底 (Auto Cap)。

3. ✂️ 革命性的曲面智能切刀 (Smart Custom Cutters)
线框转切刀：直接提取面组边界，自动生成带有厚度和延伸范围的立体切刀。

无限加点手绘切刀：在模型表面左键连续点击，即可沿曲面贴合生成自定义形状的完美切刀。

参数化微调：随时修改切刀的内缩、外延、厚度，并支持“防崩溃精确布尔 (Exact Boolean)”。

4. 🔨 智能防呆插销与批量装配 (Smart Assembly Pegs)
表面吸附打孔：鼠标在模型上点击任意位置，瞬间生成带法线对齐的插销预览。

全参数化插销：自由调节插销的段数（防滑防转）、公端底径、母端顶径、总长和端部倒角。

装配公差控制 (Tolerance)：专为 FDM 打印设计的容差膨胀，完美解决“插不进去”或“太松”的问题。

一键物理装配：一键执行复杂的布尔运算，自动识别主件（公件）与散件（母件），将插销完美融合到对应的零件中。

📦 安装指南 (Installation)
要求：Blender 4.2 或更高版本 (Requires Blender 4.2+)

下载本仓库的 .zip 压缩包。

打开 Blender，点击顶部菜单栏的 Edit (编辑) -> Preferences (偏好设置)。

在左侧选择 Get Extensions (获取扩展)。

点击右上角的向下箭头 v，选择 Install from Disk... (从磁盘安装)。

选中你下载的 .zip 文件，安装并启用。

在 3D 视图中按 N 键打开侧边栏，找到 PrintPrep (打印分件) 面板即可开始使用！

💡 快速工作流 (Quick Workflow)
定尺寸：使用面板第 1 步的工具，将模型缩放到适合你打印机的真实尺寸。

画面组/画切刀：你可以选择让插件自动计算面组，或是使用【多点定位手绘切刀】在模型表面画出分割线。

点插销：使用【点选表面生成插销】在切割面上放置几个定位销，按需调整它们的容差。

一键切分装配：点击【执行切割与圆心定位】或【物理装配执行】，去泡杯咖啡，回来后模型就已经变成了带有插口的完美打印散件！

🌍 多语言支持 (i18n Support)
本插件原生支持简体中文 (Simplified Chinese) 与 English。
界面语言会完全自动跟随你的 Blender 软件语言设置（需在偏好设置中开启 Interface (界面) 翻译选项）。
