# Blender 后端不可发射账目(逐函数落零值桩,签名保持,调用接线不受影响)

真源侧 `[ShaderCapability<T>]` 声明的、**不可能按计算等价移植**的渲染管线级差异:
割点 = 数学树只导出询问、由运行时接宿主原生等价物;折缺席值 = 本宿主答不出,
落**能力自己声明**的缺席值(不是后端挑的中性数)。

## 栈 ruri_character_uber_girlsfrontline

### 不可发射函数

| 函数 | 原因 |
|---|---|
| EyeBlendMultiply | 终点 ret_gBuffer0 依赖灯答案却接非 Light 口:宿主下沿污染路径按能力缺席值重算 |

