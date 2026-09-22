# RuriRipperImporter — 项目特化铁律

> 通用工程铁律继承 skill `ruri-engineering-discipline`,本文只放本仓特化。
> 条款与用户指令冲突或条款本身错 → 先改本文,再写代码。

## 🔴 1. 游戏特定逻辑一律不许写在 py 里

**判据:`Game/**` 里一个手写 .py 都没有。** 凡是「解析某游戏的表/名字/槽位/材质码/
LOD 规则/闭包/资产发现」这类逻辑,一律实现在:

```
D:\Ruri\Git\FractalTools\Ruri-RipperHook\Source\Ruri.RipperHook\AssetRipperGameHook
```

py 侧只经 `Kernel.bridge.session` 的四个动词拿**已经算好的结果**;一次选择「是什么」
只有一个答案:`core.statement.*`(见 `Kernel/statement.py`)。

**为什么**:python 逐资产解析是分钟级、单线程、还要跨 CLR 边界来回搬数据;同一套逻辑在
C# 侧是秒级且能并行。把逻辑放在 py 里等于给整条链装一个不可优化的天花板。
**顶级性能是硬要求,不是偏好。**

新游戏 = hook 侧新增数据集 + `Game/<游戏>/` 一个只放数据的文件夹;页签由
**数据集的角色 × 宿主能力**自动点亮,`Kernel/panels/` 一行不用改。

## 🔴 2. 层界(判据可 grep)

| 目录 | 禁止出现 |
|---|---|
| `Kernel/` | `bpy` / `mathutils` / `substance_painter` / `PySide` / 任何一个游戏的名字 |
| `Host/<宿主>/` | 另一个宿主的 API;任何游戏的名字 |
| `Game/<游戏>/` | **任何 .py**(生成的着色栈除外);只放数据 |

`Kernel/bridge/` 是读取器的唯一入口,公开面只有四个动词
(表 / 字节 / 视图 / 搜索)加会话控制;`Kernel/statement.py` 是**唯一**把字节变成数组的地方
(唯一的 `frombuffer`);`Kernel/extensions.py` 是**唯一**的注册表。
多出第二份即违规,判据是 grep。

**坐标约定一个数字都不许写在 py 里。** 基变换 `matrix`、顶层一次性转身 `root`、以及
**相机/灯自己朝哪个轴的那一下 `aim`**,全部从 `core.bases` 读(`Kernel/statement.py::basis`)。
`aim` 只落在相机/灯这一个变换上,它的**子物体要乘逆**才不会被带着转;宿主里出现
`Matrix.Rotation(pi/2, 4, "X")` 这种写法即违规 —— 那是内核的陈述,不是宿主的意见。

**宿主差异一律是能力协议**(`Kernel/capabilities.py`:Toolkit / SceneGraph / Rig /
Timeline / Director / MorphTargets / NodeMaterials / TextureSets / Display)。驱动**继承**它答得出
的那几个,`isinstance` 推出能力集——**不许声明两遍,不许写抛异常的桩**,更**禁止
`if host.name == ...`**。

## 🔴 3. 一个包两个宿主,入口不许分叉

根 `__init__.py` 只做宿主检测 + 分派:Blender 走 `register/unregister`,
Painter 走 `start_plugin/close_plugin/reload_plugin`,两边都落到 `Host/<宿主>/`。

Painter 侧的插件目录是**指向本仓的目录联接**:

```
<Painter user resources>\python\plugins\RuriRipperImporter
  -> D:\Ruri\00.Model\Tools\BlenderProfile\RuriConfig\scripts\addons\RuriRipperImporter
```

看到两条路径指向看起来一样的东西,先假设是同一个目录(`Get-Item -Force | Select LinkType, Target`)。

## 🔴 3.5 一行的 Payload 必须**就是**种子

列表里一行能被导入,靠的是它的 `ColumnRole.Payload` 列的值**直接就是内核认得的种子**
(`core.statement.*` 的 `seed` 参数)。名册给角色 id、场景表给地图名、卡片表给文件路径,
都是**把拼种子这件事推给了宿主**——而宿主不知道这个游戏的前缀,于是按钮按下去只会得到
「这个种子没人认领」。

**判据**:每个会被导入的数据集,payload 列的值拿去 `core.statement.nodes --data-arg seed=<它>`
要出行。种子的拼法写在**认领它的那个 StatementSource 旁边**(`XxxStatementSource.XxxSeed(...)`),
任何一张表都不许自己拼前缀——拼两处就是两份真源,漂移只会在按钮上现形。

**答案型数据集不许带能上页签的角色。** 一张表是「列表」还是「答案」看它的签名:参数全是
可选/可空列表 = 页签能直接打开它;有必填参数 = 它在答一个还没被挑中的东西。所以
`unity.blendshapes`(必填 `cab+`)、`endfield.npc.meshes`、`endfield.character.models`
一律把列表参数标成**必填**,`koikatu.anime.acts` 这种纯结构 join 标 `Internal`。
**判据:页签清单里不许有点开就是 0 行的项。**

**「这个表情/这个动作是什么」的表(`FacePatterns`)有固定签名**:第一个参数是**被挑中那行的
payload**,第二个(如果声明了)是**选中的骨架当初是用哪个种子建出来的**(`host.rig_seed`,
导入时烙在骨架上)。返回的行自己说明它是哪一种脸:带 `mesh/index/weight` 就是形态键,
带 `kind/ctrl/bone` + TRS 就是骨驱动,页签按列分动词,**不看游戏名**。

同理,一个页签**有没有「导入」这个动作**是页签自己声明的(`define(..., imports=False)`):
表情、动作、剧情单元都有自己的动词,它们的行不是文档能装下的东西。声明了没有,按钮就不画,
从键位或脚本调过来也是空转——**不存在一个按下去什么都不发生的按钮**。

## 🔴 4. 四个唯一

| 语义 | 唯一真源 |
|---|---|
| 注册 | `Kernel/extensions.py` 的 `ExtensionPoint`(命令、页签、图提供者、顶点腿、兑现面、灯角色、后处理、Look 分段) |
| 会话 | C# 的 `core.installs`;py 只存用户输入的那几行 |
| 导入选项 | `Kernel/options.py` 一张表;两个宿主的控件都从它生成,**禁止手写第二份** |
| reload | 根 `__init__.py` + 各驱动一份,靠模块自报 `HOLDS_PROCESS_STATE` |

判据:`grep -n '"import_\|"detail_level"' Host/` 只应命中 schema 的读取,不应命中新的字面量表。

## 🔴 5. 着色栈按宿主投影,路径不硬编码

生成物落在 `Game/<游戏>/shader/<宿主>/`,由生成器配方的 `destination` 决定
(`Ruri.RenderPipelines.Generator/Assets/Recipes/{Blender,Substance}.json`)。
消费方一律走 `Kernel/shaderstack.py` 解析,**按安装自己公布的产品名 / 引擎家族**找
`Game/<名字>/`——文件夹名就是 join,没有映射表,**代码里不许出现着色器名或游戏名**。
产物里带 `register`/`unregister` 的模块由 `shaderstack.register()` 发现并加载,
**不需要手写 `__init__.py` 门面**。

产物的清单里写着它绑定的宿主模块与函数名(`registry_module` / `register_fn` / …),
那是**产物对宿主的声明**:`Host/Blender/material_builder.py` 的那组函数名因此是数据,
改名要改配方重生成,不许单方面改宿主。

改生成物里的宿主回调路径(`RegistryModule` / `RigIdentityModule`)= **改配方再重生成**,
不许手改产物 —— 产物是配方的投影。重生成+部署:

```bash
dotnet run --project Ruri.RenderPipelines/Ruri.Generator.Cli -c Release -- --deploy-shaders Assets/Recipes/Blender.json
```

## 6. 收工验证

**画得出来 ≠ 按得下去。** `draw()` 不抛异常只说明面板画得出,命令体自己调自己这种错要等到
**真按一次**才现形。所以收工的判据是:**把注册表里每一条命令,在每一个安装上,通过它真正的
算子按一次**,记下 `ok / 异常 / 跳过理由`。跳过只有两种合法理由:①这个宿主没有那条能力
(`requires` 的协议)②本机没有那个安装。

Blender(headless 按得下去,只是画不出来):

```bash
BLENDER_USER_SCRIPTS=<测试 profile>/scripts blender.exe --background --python <探针>
```

探针里 `addon_utils` 或直接 `RuriRipperImporter.register()`,然后
`getattr(bpy.ops, ns).op("EXEC_DEFAULT", **arguments)` 逐条按。stepped 的命令在无窗口时
自己走 inline 驱动,和交互式走的是同一个生成器。

Painter(不能 headless):最接近的可跑检查是把 `substance_painter` / `PySide6` 打桩后
真 import 整棵驱动树 —— 模块体全部执行,宿主绑定、设置表按 schema 建键、选项控件按 schema 建出来,
再对同一份命令清单逐条 `run`。真 API 语义仍然只能开 GUI 验。

静态尺三把(纯 AST,不 import,所以缺宿主 API 也能跑):未定义全局名、跨模块不存在的属性、
**指向已删模块的相对 import**(函数体里的 `from ...Gone import x` 只有它抓得到)。
