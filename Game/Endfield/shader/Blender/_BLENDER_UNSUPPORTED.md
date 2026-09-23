# Blender 后端不可发射账目(逐函数落零值桩,签名保持,调用接线不受影响)

真源侧 `[ShaderCapability<T>]` 声明的、**不可能按计算等价移植**的渲染管线级差异:
割点 = 数学树只导出询问、由运行时接宿主原生等价物;折缺席值 = 本宿主答不出,
落**能力自己声明**的缺席值(不是后端挑的中性数)。

## 栈 ruri_character_uber_endfield

### 宿主答不出的环境询问(按缺席值折叠)

| 能力 | 答案来源 | 缺席契约 | 结果语义 | 编译器为什么认不出 |
|---|---|---|---|---|
| ScreenDepth | Pipeline | Declared | raw device depth | reversed-Z / 线性 / 对数深度三种约定并存,_ZBufferParams 的打包也是引擎私有;而材质节点图读不到深度缓冲 |
| ScreenSpaceShadowMask | Pipeline | Identity | [0,1] screen-space resolved shadow mask | 解算通道数与语义各家自定(HG 是 .x 场景 / .y 角色图集),而且它是本帧的一张 RT;编译器看见的只是一次按屏幕坐标的纹理取值 |

### 不可发射函数

| 函数 | 原因 |
|---|---|
| OverlayShadow | 终点 ret_gBuffer0 依赖灯答案却接非 Light 口:宿主下沿污染路径按能力缺席值重算 |
| EndfieldCharaGBufferPassVertex[OverlayShadow] | uniform UNITY_MATRIX_P 为结构/资源型(float4x4),无节点图等价 |

## 栈 ruri_scene_uber_endfield

### 宿主答不出的环境询问(按缺席值折叠)

| 能力 | 答案来源 | 缺席契约 | 结果语义 | 编译器为什么认不出 |
|---|---|---|---|---|
| ScreenColor | Pipeline | Declared | linear scene radiance | 有的管线是 RT 有的是 copy,分辨率/mip 链/色彩空间各不相同;而材质节点图**根本读不到**已绘制的帧缓冲 |
| ScreenDepth | Pipeline | Declared | raw device depth | reversed-Z / 线性 / 对数深度三种约定并存,_ZBufferParams 的打包也是引擎私有;而材质节点图读不到深度缓冲 |

### 不可发射函数

| 函数 | 原因 |
|---|---|
| SampleNormalMap | uniform _UseBumpMap 挂 [ShaderProperty] 但 Default 缺失/不可解析——禁止发明默认值 |

## 栈 ruri_effect_uber_endfield

### 宿主答不出的环境询问(按缺席值折叠)

| 能力 | 答案来源 | 缺席契约 | 结果语义 | 编译器为什么认不出 |
|---|---|---|---|---|
| ScreenColor | Pipeline | Declared | linear scene radiance | 有的管线是 RT 有的是 copy,分辨率/mip 链/色彩空间各不相同;而材质节点图**根本读不到**已绘制的帧缓冲 |
| ScreenDepth | Pipeline | Declared | raw device depth | reversed-Z / 线性 / 对数深度三种约定并存,_ZBufferParams 的打包也是引擎私有;而材质节点图读不到深度缓冲 |

### 不可发射函数

| 函数 | 原因 |
|---|---|
| texture3D | _NoiseTex3D:宿主无 3D 纹理节点,按槽中性值直通 |

