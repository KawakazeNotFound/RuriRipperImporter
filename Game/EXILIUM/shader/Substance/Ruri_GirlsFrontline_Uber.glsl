//============================================================================
// Ruri_GirlsFrontline_Uber.glsl —— 生成物,勿手改(真源 = Ruri.RenderPipelines.Generator C# 材质模块)
// 风格 = GirlsFrontline;输入投影清单 = Ruri_GirlsFrontline_Uber.manifest.json(导入器与本文件同源同构)
//============================================================================

//----------------------------------------------------------------------region HLSL→GLSL 词法桥(生成物,勿手改)
#define float2 vec2
#define float3 vec3
#define float4 vec4
#define half float
#define half2 vec2
#define half3 vec3
#define half4 vec4
#define float2x2 mat2
#define float3x3 mat3
#define float4x4 mat4
#define half3x3 mat3
#define half4x4 mat4
#define uint2 uvec2
#define uint3 uvec3
#define uint4 uvec4
#define int2 ivec2
#define int3 ivec3
#define int4 ivec4
#define bool2 bvec2
#define bool3 bvec3
#define bool4 bvec4

#define frac fract
#define ddx dFdx
#define ddy dFdy
#define fmod mod
#define atan2(y, x) atan(y, x)
#define rsqrt inversesqrt
#define asuint floatBitsToUint
#define asfloat uintBitsToFloat
#define asint floatBitsToInt
#define UNITY_BRANCH
#define UNITY_LOOP
#define UNITY_FLATTEN

float  saturate(float v)  { return clamp(v, 0.0, 1.0); }
vec2   saturate(vec2 v)   { return clamp(v, vec2(0.0), vec2(1.0)); }
vec3   saturate(vec3 v)   { return clamp(v, vec3(0.0), vec3(1.0)); }
vec4   saturate(vec4 v)   { return clamp(v, vec4(0.0), vec4(1.0)); }

float  lerp(float a, float b, float t) { return mix(a, b, t); }
vec2   lerp(vec2 a, vec2 b, float t)   { return mix(a, b, t); }
vec3   lerp(vec3 a, vec3 b, float t)   { return mix(a, b, t); }
vec4   lerp(vec4 a, vec4 b, float t)   { return mix(a, b, t); }
vec2   lerp(vec2 a, vec2 b, vec2 t)    { return mix(a, b, t); }
vec3   lerp(vec3 a, vec3 b, vec3 t)    { return mix(a, b, t); }
vec4   lerp(vec4 a, vec4 b, vec4 t)    { return mix(a, b, t); }

float  mad(float a, float b, float c) { return a * b + c; }
vec2   mad(vec2 a, vec2 b, vec2 c)    { return a * b + c; }
vec3   mad(vec3 a, vec3 b, vec3 c)    { return a * b + c; }
vec4   mad(vec4 a, vec4 b, vec4 c)    { return a * b + c; }
vec2   mad(vec2 a, float b, vec2 c)   { return a * b + c; }
vec3   mad(vec3 a, float b, vec3 c)   { return a * b + c; }
vec4   mad(vec4 a, float b, vec4 c)   { return a * b + c; }

// HLSL mul 语义(矩阵按逻辑布局搬运:行构造经 ruriMatRows 转置,列语义两侧一致)。
// 本组是 mul 的**唯一供给**:同名 C# 镜像一律不编译(见 SubstanceDialect.BridgedNames 派生),
// 故镜像里出现过的每个重载都必须在这里齐备 —— 少一个 = 调用点无匹配重载。
vec3   mul(mat3 m, vec3 v)  { return m * v; }
vec4   mul(mat4 m, vec4 v)  { return m * v; }
vec3   mul(mat4 m, vec3 v)  { return mat3(m) * v; }
vec3   mul(vec3 v, mat3 m)  { return v * m; }
vec4   mul(vec4 v, mat4 m)  { return v * m; }
vec3   mul(vec3 v, mat4 m)  { return v * mat3(m); }
mat3   mul(mat3 a, mat3 b)  { return a * b; }
mat4   mul(mat4 a, mat4 b)  { return a * b; }

mat3   ruriMat3Rows(vec3 r0, vec3 r1, vec3 r2) { return transpose(mat3(r0, r1, r2)); }
mat4   ruriMat4Rows(vec4 r0, vec4 r1, vec4 r2, vec4 r3) { return transpose(mat4(r0, r1, r2, r3)); }

float  rcp(float x) { return 1.0 / x; }
vec2   rcp(vec2 x)  { return vec2(1.0) / x; }
vec3   rcp(vec3 x)  { return vec3(1.0) / x; }
vec4   rcp(vec4 x)  { return vec4(1.0) / x; }

void clip(float x) { if (x < 0.0) discard; }
void clip(vec4 x)  { if (any(lessThan(x, vec4(0.0)))) discard; }

// 附加光循环(URP 非聚簇形;灯数经能力兑现,缺席=0 → 死循环体被编译器消除)。
#define LIGHT_LOOP_BEGIN(count) for (uint lightIndex = 0u; lightIndex < count; ++lightIndex) {
#define LIGHT_LOOP_END }

// sRGB 解码(宿主原样槽位的颜色纹理:裸采样无硬件解码,按声明补;alpha 不解码)。
float ruriSrgbToLinear(float c) {
    return (c <= 0.04045) ? (c / 12.92) : pow(abs((c + 0.055) / 1.055), 2.4);
}
vec4 ruriSampleSrgb(sampler2D t, vec2 uv) {
    vec4 s = texture(t, uv);
    return vec4(ruriSrgbToLinear(s.r), ruriSrgbToLinear(s.g), ruriSrgbToLinear(s.b), s.a);
}
vec4 ruriSampleSrgbLod(sampler2D t, vec2 uv, float lod) {
    vec4 s = textureLod(t, uv, lod);
    return vec4(ruriSrgbToLinear(s.r), ruriSrgbToLinear(s.g), ruriSrgbToLinear(s.b), s.a);
}

// CLAMP 寻址复现(ramp/LUT 声明为 Clamp 的纹理:钳到 texel 中心,双线性不吃边框)。
vec2 ruriUvClamp(sampler2D t, vec2 uv) {
    vec2 size = vec2(textureSize(t, 0));
    vec2 halfTexel = 0.5 / max(size, vec2(1.0));
    return clamp(uv, halfTexel, vec2(1.0) - halfTexel);
}
//----------------------------------------------------------------------endregion

//----------------------------------------------------------------------region 面板参数(生成)
//: param custom { "default": 0, "label": "GirlsFrontline Part", "widget": "combobox", "values": { "0 Standard": 0, "1 Face": 1, "2 Eyes": 2, "3 EyeBlendAdd": 3, "4 EyeBlendMultiply": 4 }, "group": "0 部位" }
uniform_specialization int _CharaPartID;
//: param custom { "default": 0.31830987, "label": "INV_PI", "group": "R 引擎态" }
uniform float INV_PI;
//: param custom { "default": 0, "label": "Anisotropic GGX", "min": -1, "max": 1, "group": "Stocking" }
uniform float _AnisotropicGXX;
//: param custom { "default": false, "label": "Use Anisotropic Specular", "group": "Stocking" }
uniform bool _AnisotropicSpecular;
//: param custom { "default": 1, "label": "Anisotropy", "min": 0, "max": 5, "group": "参数" }
uniform float _Anisotropy;
//: param custom { "default": 0.05, "label": "Anisotropy Shift", "min": 0, "max": 1, "group": "参数" }
uniform float _AnisotropyShift;
//: param custom { "default": [1, 1, 1, 1], "label": "Color", "widget": "color", "srgb": true, "group": "参数" }
uniform vec4 _BaseColor;
//: param custom { "default": 0.1, "label": "Blend Smoothness", "min": 0, "max": 1, "group": "Stocking" }
uniform float _BlendSmoothness;
//: param custom { "default": 1, "label": "Normal Scale", "group": "参数" }
uniform float _BumpScale;
//: param custom { "default": 0.3, "label": "Cornea Parallax", "min": 0, "max": 0.5, "group": "Character Effect" }
uniform float _CorneaParallax;
//: param custom { "default": 0.15, "label": "Alpha Cutoff", "min": 0, "max": 1, "group": "State" }
uniform float _Cutoff;
//: param custom { "default": 1, "label": "Emissive Intensity", "min": 1, "max": 20, "group": "参数" }
uniform float _EmissiveIntensity;
//: param custom { "default": 0, "label": "_WetFlowSize", "group": "Character Effect" }
uniform float _FaceLightDirAdjustment;
//: param custom { "default": [1, 1, 1, 1], "label": "Final Tint", "widget": "color", "srgb": true, "group": "Character Effect" }
uniform vec4 _FinalTint;
//: param custom { "default": [1, 1, 1, 0.85], "label": "Main Color", "widget": "color", "srgb": true, "group": "Character Effect" }
uniform vec4 _MainColor;
const uint _MainLightLayerMask = uint(0xFFFFFFFF);
//: param custom { "default": [1, 1, 1, 1], "label": "_MainLightOcclusionProbes", "group": "R 引擎态" }
uniform vec4 _MainLightOcclusionProbes;
//: param custom { "default": 1, "label": "Metallic Intensity", "group": "参数" }
uniform float _MetallicIntensity;
//: param custom { "default": 1, "label": "Roughness Intensity", "group": "参数" }
uniform float _RoughnessIntensity;
//: param custom { "default": 0.25, "label": "Shadow Intensity", "min": 0, "max": 1, "group": "Character Effect" }
uniform float _ShadowIntensity;
//: param custom { "default": 1, "label": "Specular Intensity", "group": "参数" }
uniform float _SpecularIntensity;
//: param custom { "default": 0.3, "label": "Specular Parallax", "min": 0, "max": 1, "group": "Character Effect" }
uniform float _SpecularParallax;
//: param custom { "default": [1, 1, 1, 1], "label": "Stocking Center Color", "widget": "color", "srgb": true, "group": "参数" }
uniform vec4 _StockingCenterColor;
//: param custom { "default": [0.1, 0, 0, 1], "label": "Stocking Falloff Color", "widget": "color", "srgb": true, "group": "参数" }
uniform vec4 _StockingFalloffColor;
//: param custom { "default": 1, "label": "Stocking Falloff Power", "min": 0.1, "max": 5, "group": "参数" }
uniform float _StockingFalloffPower;
//: param custom { "default": 0, "label": "Surface Type", "min": 0, "max": 1, "group": "参数" }
uniform int _SurfaceType;
//: param custom { "default": false, "label": "Use Alpha Test", "group": "State" }
uniform bool _UseAlphaTest;
//: param custom { "default": false, "label": "Use RMOS Map", "group": "参数" }
uniform bool _UseRMOSMap;
//: param custom { "default": false, "label": "Use Ramp Map", "group": "参数" }
uniform bool _UseRampMap;
//: param custom { "default": false, "label": "Use UV2", "group": "Stocking" }
uniform bool _UseSpecularUV2;
//: param custom { "default": false, "label": "Use Stocking Falloff", "group": "Stocking" }
uniform bool _UseStockingFalloff;
//: param custom { "default": [1, 1, 0, 0], "label": "unity_SpecCube0_HDR", "group": "R 引擎态" }
uniform vec4 unity_SpecCube0_HDR;
//----------------------------------------------------------------------endregion

//----------------------------------------------------------------------region 宿主库
import lib-pbr.glsl
import lib-bent-normal.glsl
import lib-emissive.glsl
import lib-sss.glsl
import lib-utils.glsl
import lib-sparse.glsl
//----------------------------------------------------------------------endregion

//: state cull_face off
//: state blend over

//: param auto camera_view_matrix
uniform mat4 uniform_camera_view_matrix;
//: param auto environment_max_lod
uniform float environment_max_lod;
//: param auto facing
uniform int uniform_facing;
//: param auto main_light
uniform vec4 light_main;

//----------------------------------------------------------------------region 宿主输入(投影方案派生)
//: param auto channel_basecolor
uniform SamplerSparse basecolor_tex;
//: param auto channel_opacity
uniform SamplerSparse opacity_tex;
//: param custom { "default": "", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "Blend Tex", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _BlendTex;
//: param auto channel_user1
uniform SamplerSparse slot_user1_tex;
//: param custom { "default": "", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "MainTex", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _MainTex;
//: param auto channel_roughness
uniform SamplerSparse roughness_tex;
//: param auto channel_metallic
uniform SamplerSparse metallic_tex;
//: param auto channel_specularlevel
uniform SamplerSparse specularlevel_tex;
//: param custom { "default": "", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "RMO Map (RGB)", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _RMOTex;
//: param custom { "default": "", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "Diffuse Ramp Map", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _RampMap;
//: param custom { "default": "", "default_color": [0.0, 0.0, 0.0, 0.0], "label": "Specular Map", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _Specularmap;
//: param custom { "default": "", "default_color": [1.0, 1.0, 1.0, 1.0], "label": "_BumpMap 余量(ba)", "usage": "texture", "group": "2 贴图" }
uniform sampler2D _BumpMap_ba;
//----------------------------------------------------------------------endregion

#ifndef RURI_PRELUDE_RURILENGTH
#define RURI_PRELUDE_RURILENGTH
float ruriLength(float2 v) { return sqrt(dot(v, v)); }
float ruriLength(float3 v) { return sqrt(dot(v, v)); }
float ruriLength(float4 v) { return sqrt(dot(v, v)); }
#endif

#ifndef RURI_PRELUDE_RURINORMALIZE
#define RURI_PRELUDE_RURINORMALIZE
float2 ruriNormalize(float2 v) { return v / sqrt(dot(v, v)); }
float3 ruriNormalize(float3 v) { return v / sqrt(dot(v, v)); }
float4 ruriNormalize(float4 v) { return v / sqrt(dot(v, v)); }
#endif

//----------------------------------------------------------------------region 结构体
struct CharaVaryings {
    vec2 uv;
    vec3 positionWS;
    vec3 normalWS;
    vec4 tangentWS;
    vec4 uv1;
    vec2 uv0zw;
    vec4 positionNDC;
    vec4 color;
    vec4 positionCS;
};

struct GBufferData {
    vec3 baseColor;
    float smoothness;
    vec3 specularColor;
    float occlusion;
    vec3 normalWS;
    uint materialFlags;
    float depth;
    vec4 shadowMask;
    uint meshRenderingLayers;
};

struct GBufferFragOutput {
    vec4 gBuffer0;
    vec4 gBuffer1;
    vec4 gBuffer2;
    vec4 color;
    float depth;
    vec4 shadowMask;
    uint meshRenderingLayers;
};

struct Light {
    vec3 direction;
    vec3 color;
    float distanceAttenuation;
    float shadowAttenuation;
    uint layerMask;
};

struct RuriData {
    float alpha;
    vec3 albedo;
    float roughness;
    float metallic;
    float occlusion;
    float specular;
    vec3 normalTS;
    vec3 positionWS;
    vec4 positionCS;
    vec3 normalWS;
    vec3 viewDirectionWS;
    vec4 shadowCoord;
    vec3 bakedGI;
    vec2 normalizedScreenSpaceUV;
    vec4 shadowMask;
    float diffuse;
    vec4 baseSample;
    float baseAlpha;
    vec3 V;
    vec3 L;
    vec3 H;
    vec3 camFwd;
    Light mainLight;
    vec3 adjustedLightDir;
    float adjXZ_x;
    float adjXZ_z;
    float adjXZLen;
    float camLightDotRaw;
    float camLightDot;
    float camYSmooth;
    float exposure;
    float ambInt;
    float perObjectShadow;
    float useRampVal;
    float specScale;
    float base_weight;
    vec3 base_color;
    float base_diffuse_roughness;
    float base_metalness;
    float specular_weight;
    vec3 specular_color;
    float specular_roughness;
    float specular_ior;
    float specular_roughness_anisotropy;
    float subsurface_weight;
    vec3 subsurface_color;
    float subsurface_radius;
    vec3 subsurface_radius_scale;
    float subsurface_scatter_anisotropy;
    float fuzz_weight;
    vec3 fuzz_color;
    float fuzz_roughness;
    float coat_weight;
    vec3 coat_color;
    float coat_roughness;
    float coat_roughness_anisotropy;
    float coat_ior;
    float coat_darkening;
    float emission_luminance;
    vec3 emission_color;
    vec3 coat_normal;
};

struct RuriGBufferData {
    float alpha;
    vec3 baseColor;
    float roughness;
    float metallic;
    float occlusion;
    float specular;
    float lightBlock;
    float lightSky;
    uint materialFlags;
    uint shadingModel;
    vec4 customData;
    vec3 normalWS;
    float depth;
    vec4 shadowMask;
    uint meshRenderingLayers;
    vec4 globalIllumination;
};

struct SceneVaryings {
    vec2 uv;
    vec3 positionWS;
    vec3 positionOS;
    vec3 normalWS;
    vec4 tangentWS;
    vec2 voxelUV;
    vec3 voxelLitColor;
    vec2 staticLightmapUV;
    vec4 positionNDC;
    vec4 color;
    vec2 voxelSliceMaterial;
    vec2 voxelMaterialIris;
    vec2 uv1;
    vec2 uv2;
    vec2 voxelBlockLight;
    vec4 positionCS;
};

//----------------------------------------------------------------------endregion

//----------------------------------------------------------------------region 结构零值
CharaVaryings ruriZeroCharaVaryings() {
    CharaVaryings v;
    v.uv = vec2(0.0);
    v.positionWS = vec3(0.0);
    v.normalWS = vec3(0.0);
    v.tangentWS = vec4(0.0);
    v.uv1 = vec4(0.0);
    v.uv0zw = vec2(0.0);
    v.positionNDC = vec4(0.0);
    v.color = vec4(0.0);
    v.positionCS = vec4(0.0);
    return v;
}

GBufferFragOutput ruriZeroGBufferFragOutput() {
    GBufferFragOutput v;
    v.gBuffer0 = vec4(0.0);
    v.gBuffer1 = vec4(0.0);
    v.gBuffer2 = vec4(0.0);
    v.color = vec4(0.0);
    v.depth = 0.0;
    v.shadowMask = vec4(0.0);
    v.meshRenderingLayers = uint(0);
    return v;
}

Light ruriZeroLight() {
    Light v;
    v.direction = vec3(0.0);
    v.color = vec3(0.0);
    v.distanceAttenuation = 0.0;
    v.shadowAttenuation = 0.0;
    v.layerMask = uint(0);
    return v;
}

RuriData ruriZeroRuriData() {
    RuriData v;
    v.alpha = 0.0;
    v.albedo = vec3(0.0);
    v.roughness = 0.0;
    v.metallic = 0.0;
    v.occlusion = 0.0;
    v.specular = 0.0;
    v.normalTS = vec3(0.0);
    v.positionWS = vec3(0.0);
    v.positionCS = vec4(0.0);
    v.normalWS = vec3(0.0);
    v.viewDirectionWS = vec3(0.0);
    v.shadowCoord = vec4(0.0);
    v.bakedGI = vec3(0.0);
    v.normalizedScreenSpaceUV = vec2(0.0);
    v.shadowMask = vec4(0.0);
    v.diffuse = 0.0;
    v.baseSample = vec4(0.0);
    v.baseAlpha = 0.0;
    v.V = vec3(0.0);
    v.L = vec3(0.0);
    v.H = vec3(0.0);
    v.camFwd = vec3(0.0);
    v.mainLight = ruriZeroLight();
    v.adjustedLightDir = vec3(0.0);
    v.adjXZ_x = 0.0;
    v.adjXZ_z = 0.0;
    v.adjXZLen = 0.0;
    v.camLightDotRaw = 0.0;
    v.camLightDot = 0.0;
    v.camYSmooth = 0.0;
    v.exposure = 0.0;
    v.ambInt = 0.0;
    v.perObjectShadow = 0.0;
    v.useRampVal = 0.0;
    v.specScale = 0.0;
    v.base_weight = 0.0;
    v.base_color = vec3(0.0);
    v.base_diffuse_roughness = 0.0;
    v.base_metalness = 0.0;
    v.specular_weight = 0.0;
    v.specular_color = vec3(0.0);
    v.specular_roughness = 0.0;
    v.specular_ior = 0.0;
    v.specular_roughness_anisotropy = 0.0;
    v.subsurface_weight = 0.0;
    v.subsurface_color = vec3(0.0);
    v.subsurface_radius = 0.0;
    v.subsurface_radius_scale = vec3(0.0);
    v.subsurface_scatter_anisotropy = 0.0;
    v.fuzz_weight = 0.0;
    v.fuzz_color = vec3(0.0);
    v.fuzz_roughness = 0.0;
    v.coat_weight = 0.0;
    v.coat_color = vec3(0.0);
    v.coat_roughness = 0.0;
    v.coat_roughness_anisotropy = 0.0;
    v.coat_ior = 0.0;
    v.coat_darkening = 0.0;
    v.emission_luminance = 0.0;
    v.emission_color = vec3(0.0);
    v.coat_normal = vec3(0.0);
    return v;
}

RuriGBufferData ruriZeroRuriGBufferData() {
    RuriGBufferData v;
    v.alpha = 0.0;
    v.baseColor = vec3(0.0);
    v.roughness = 0.0;
    v.metallic = 0.0;
    v.occlusion = 0.0;
    v.specular = 0.0;
    v.lightBlock = 0.0;
    v.lightSky = 0.0;
    v.materialFlags = uint(0);
    v.shadingModel = uint(0);
    v.customData = vec4(0.0);
    v.normalWS = vec3(0.0);
    v.depth = 0.0;
    v.shadowMask = vec4(0.0);
    v.meshRenderingLayers = uint(0);
    v.globalIllumination = vec4(0.0);
    return v;
}

//----------------------------------------------------------------------endregion

SparseCoord ruriSparseCoord;

//----------------------------------------------------------------------region 宿主胶水(配方)
//: param custom { "default": 0, "label": "灯光旋转 X", "min": 0, "max": 360, "group": "0 光照" }
uniform int i_LightRotX;
//: param custom { "default": 30, "label": "灯光旋转 Y", "min": 0, "max": 360, "group": "0 光照" }
uniform int i_LightRotY;
//: param custom { "default": 0, "label": "灯光旋转 Z", "min": 0, "max": 360, "group": "0 光照" }
uniform int i_LightRotZ;
//: param custom { "default": [1.0, 1.0, 1.0], "label": "主光颜色", "widget": "color", "group": "0 光照" }
uniform vec3 v_MainLightColor;
//: param custom { "default": 0.0, "label": "时间 Time", "min": 0.0, "max": 100.0, "group": "0 光照" }
uniform float f_RuriTime;
mat3 ruriRotX(float r) { float c = cos(r), s = sin(r); return mat3(1,0,0, 0,c,s, 0,-s,c); }
mat3 ruriRotY(float r) { float c = cos(r), s = sin(r); return mat3(c,0,-s, 0,1,0, s,0,c); }
mat3 ruriRotZ(float r) { float c = cos(r), s = sin(r); return mat3(c,s,0, -s,c,0, 0,0,1); }
// 物体→世界。本宿主一棵着色器服务整个模型,没有「物体」可问,所以这三列由桥算好随材质行过来(它同时知道物体摆位、负载根节点为对齐 Y 轴带的旋转、以及两种物体空间约定之间的 Y/Z 互换——那是个反射不是旋转,所以假定单位阵不是「转错了」而是「左右反了」)。缺省是单位阵:没人告诉就跟从前一模一样。
//: param custom { "default": [1, 0, 0, 0], "label": "物体→世界 列0", "group": "R 引擎态" }
uniform vec4 i_ObjectToWorld0;
//: param custom { "default": [0, 1, 0, 0], "label": "物体→世界 列1", "group": "R 引擎态" }
uniform vec4 i_ObjectToWorld1;
//: param custom { "default": [0, 0, 1, 0], "label": "物体→世界 列2", "group": "R 引擎态" }
uniform vec4 i_ObjectToWorld2;
mat4 ruriObjectToWorld() {
    return mat4(i_ObjectToWorld0, i_ObjectToWorld1, i_ObjectToWorld2, vec4(0.0, 0.0, 0.0, 1.0));
}
vec3 ruriMainLightDir() {
    mat3 rot = ruriRotY(radians(float(i_LightRotY))) * ruriRotX(radians(float(i_LightRotX))) * ruriRotZ(radians(float(i_LightRotZ)));
    return normalize(rot * light_main.xyz);
}
// 单趟等价:F 腿回读的 gbuffer 就是本表面 G 腿写入的自身数据 —— 直接用本片元的表面态回声。
GBufferData ruriSelfGBuffer(RuriData rd) {
    GBufferData g;
    g.baseColor = rd.albedo;
    g.smoothness = 1.0 - rd.roughness;
    g.specularColor = vec3(rd.specular);
    g.occlusion = rd.occlusion;
    g.normalWS = rd.normalWS;
    g.materialFlags = 0u;
    g.depth = 0.0;
    g.shadowMask = vec4(1.0);
    g.meshRenderingLayers = 0u;
    return g;
}

// LinearToSRGB:URP 内建。其 C# 镜像的 float3 重载体是**向真身的委托** —— Unity 腿从不发射该函数
// (URP include 提供),故自递归在那边是不可见的潜伏项;本宿主内联镜像即 'Recursion detected'。
// 由宿主前导件兑现,名字进 HostProvides 后镜像不再编译。
float LinearToSRGB(float c) { return (c <= 0.0031308) ? (c * 12.9232102) : (1.055 * pow(abs(c), 1.0 / 2.4) - 0.055); }
vec3 LinearToSRGB(vec3 c) { return vec3(LinearToSRGB(c.r), LinearToSRGB(c.g), LinearToSRGB(c.b)); }
//----------------------------------------------------------------------endregion

//----------------------------------------------------------------------region 引擎态兑现(配方)
#define UNITY_MATRIX_I_V (inverse(uniform_camera_view_matrix))
#define UNITY_MATRIX_M (ruriObjectToWorld())
#define UNITY_MATRIX_V (uniform_camera_view_matrix)
#define _MainLightColor (vec4(v_MainLightColor, 1.0))
#define _MainLightPosition (vec4(ruriMainLightDir(), 0.0))
#define _ScaledScreenParams (vec4(1920.0, 1080.0, 1.0 + 1.0/1920.0, 1.0 + 1.0/1080.0))
#define _WorldSpaceCameraPos (camera_pos)
#define unity_LightData (vec4(0.0, 0.0, 1.0, 0.0))
#define unity_OrthoParams (vec4(0.0, 0.0, 0.0, 0.0))
#define unity_WorldTransformParams (vec4(0.0, 0.0, 0.0, 1.0))
//----------------------------------------------------------------------endregion

//----------------------------------------------------------------------region 投影读函数(源纹理 → 宿主输入重建;与清单同源)
// 宿主可绘制通道按网格参数化取值,uv 实参不参与(源侧 ST 平铺对这些通道无效 —— 清单已披露)。
float4 ruriRead_BaseMap(float2 uv) {
    return float4((getBaseColor(basecolor_tex, ruriSparseCoord)).x, (getBaseColor(basecolor_tex, ruriSparseCoord)).y, (getBaseColor(basecolor_tex, ruriSparseCoord)).z, getOpacity(opacity_tex, ruriSparseCoord));
}

float4 ruriRead_BumpMap(float2 uv) {
    return float4(((getTSNormal(ruriSparseCoord)).x * 0.5 + 0.5), ((getTSNormal(ruriSparseCoord)).y * 0.5 + 0.5), (texture(_BumpMap_ba, uv)).x, (texture(_BumpMap_ba, uv)).y);
}

float4 ruriRead_RMOSMap(float2 uv) {
    return float4(getRoughness(roughness_tex, ruriSparseCoord), getMetallic(metallic_tex, ruriSparseCoord), getAO(ruriSparseCoord, true, use_bent_normal), getSpecularLevel(specularlevel_tex, ruriSparseCoord));
}

//----------------------------------------------------------------------endregion

vec3 UnpackNormalScale(vec4 packedNormal, float bumpScale)
{
    packedNormal.w *= packedNormal.x;
    vec3 normal;
    normal.x = packedNormal.w * 2.0 - 1.0;
    normal.y = packedNormal.y * 2.0 - 1.0;
    normal.z = max(1.0e-16, sqrt(1.0 - saturate(normal.x * normal.x + normal.y * normal.y)));
    normal.x *= bumpScale;
    normal.y *= bumpScale;
    return normal;
}

vec3 SampleNormal(vec2 uv, sampler2D bumpMap, float scale)
{
    if (_UseBumpMap)
    {
        vec4 n = vec4(texture(bumpMap, uv));
        return vec3(UnpackNormalScale(n, scale));
    }
    else
    {
        return half3(0.0, 0.0, 1.0);
    }
}

vec3 NormalizeNormalPerPixel(vec3 n)
{
    return ruriNormalize(n);
}

vec3 TransformTangentToWorld(vec3 directionTS, mat3 tangentToWorld)
{
    return mul(directionTS, tangentToWorld);
}

vec3 ResolveNormalWS(vec3 normalTS, vec3 positionWS, vec3 vertexNormalWS, vec4 tangentWS, vec2 uv)
{
    vec3 N = vec3(NormalizeNormalPerPixel(vertexNormalWS));
    vec3 dp1 = ddx(positionWS);
    vec3 dp2 = ddy(positionWS);
    vec2 duv1 = ddx(uv);
    vec2 duv2 = ddy(uv);
    vec3 T;
    vec3 B;
    if (dot(tangentWS.xyz, tangentWS.xyz) > 1e-4)
    {
        T = tangentWS.xyz;
        B = tangentWS.w * cross(N, T);
    }
    else
    {
        vec3 dp2perp = cross(dp2, N);
        vec3 dp1perp = cross(N, dp1);
        vec3 Td = dp2perp * duv1.x + dp1perp * duv2.x;
        vec3 Bd = dp2perp * duv1.y + dp1perp * duv2.y;
        float invmax = rsqrt(max(dot(Td, Td), dot(Bd, Bd)) + 1e-8);
        T = vec3(Td * invmax);
        B = vec3(Bd * invmax);
    }
    return vec3(NormalizeNormalPerPixel(TransformTangentToWorld(normalTS, ruriMat3Rows(T, B, N))));
}

bool IsPerspectiveProjection()
{
    return unity_OrthoParams.w == 0.0;
}

vec3 GetCameraPositionWS()
{
    return _WorldSpaceCameraPos;
}

vec3 GetCurrentViewPosition()
{
    return GetCameraPositionWS();
}

vec3 GetViewForwardDir()
{
    vec3 row2 = float3(UNITY_MATRIX_V[0].z, UNITY_MATRIX_V[1].z, UNITY_MATRIX_V[2].z);
    return -row2;
}

vec3 GetWorldSpaceNormalizeViewDir(vec3 positionWS)
{
    if (IsPerspectiveProjection())
    {
        vec3 V = GetCurrentViewPosition() - positionWS;
        return ruriNormalize(V);
    }
    return -GetViewForwardDir();
}

vec4 GetScaledScreenParams()
{
    return _ScaledScreenParams;
}

vec2 GetNormalizedScreenSpaceUV(vec2 positionCS)
{
    vec2 normalizedScreenSpaceUV = positionCS * (GetScaledScreenParams().zw - 1.0);
    return normalizedScreenSpaceUV;
}

vec2 GetNormalizedScreenSpaceUV(vec4 positionCS)
{
    return GetNormalizedScreenSpaceUV(positionCS.xy);
}

vec3 SampleNormal_BumpMap(vec2 uv, float scale)
{
    if (_UseBumpMap)
    {
        vec4 n = vec4(ruriRead_BumpMap(uv));
        return vec3(UnpackNormalScale(n, scale));
    }
    else
    {
        return half3(0.0, 0.0, 1.0);
    }
}

void RURI_INIT_COMMON(CharaVaryings input_, out RuriData outRuriData)
{
    outRuriData = ruriZeroRuriData();
    vec4 albedoAlpha = ruriRead_BaseMap(input_.uv);
    outRuriData.alpha = albedoAlpha.w;
    outRuriData.albedo = albedoAlpha.xyz;
    outRuriData.normalTS = SampleNormal_BumpMap(input_.uv, _BumpScale);
    outRuriData.positionCS = input_.positionCS;
    outRuriData.positionWS = input_.positionWS;
    outRuriData.normalWS = ResolveNormalWS(outRuriData.normalTS, input_.positionWS, input_.normalWS, input_.tangentWS, input_.uv);
    outRuriData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input_.positionWS);
    outRuriData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input_.positionCS);
    outRuriData.shadowMask = float4(1.0, 1.0, 1.0, 1.0);
}

void RURI_INIT_COMMON(SceneVaryings input_, out RuriData outRuriData)
{
    outRuriData = ruriZeroRuriData();
    outRuriData.alpha = 1.0;
    outRuriData.albedo = half3(1.0, 1.0, 1.0);
    outRuriData.normalTS = float3(0.0, 0.0, 1.0);
    outRuriData.positionCS = input_.positionCS;
    outRuriData.positionWS = input_.positionWS;
    outRuriData.normalWS = ResolveNormalWS(outRuriData.normalTS, input_.positionWS, input_.normalWS, input_.tangentWS, input_.uv);
    outRuriData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input_.positionWS);
    outRuriData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input_.positionCS);
    outRuriData.shadowMask = float4(1.0, 1.0, 1.0, 1.0);
}

void RURI_SHADOW_COORD(inout RuriData outRuriData)
{
    outRuriData.shadowCoord = vec4(0.0);
}

void InitializeCharaData(CharaVaryings input_, out RuriData outRuriData)
{
    RURI_INIT_COMMON(input_, outRuriData);
    if (_UseRMOSMap)
    {
        vec4 rmosMap = ruriRead_RMOSMap(input_.uv);
        outRuriData.roughness = rmosMap.x;
        outRuriData.metallic = rmosMap.y;
        outRuriData.occlusion = rmosMap.z;
        outRuriData.specular = rmosMap.w;
    }
    RURI_SHADOW_COORD(outRuriData);
    outRuriData.bakedGI = half3(0, 0, 0);
}

// ---- 主光 ----

Light GetMainLight()
{
    Light light = ruriZeroLight();
    light.direction = _MainLightPosition.xyz;
    light.distanceAttenuation = unity_LightData.z;
    light.shadowAttenuation = 1.0;
    light.color = _MainLightColor.xyz;
    light.layerMask = _MainLightLayerMask;
    return light;
}

float MainLightRealtimeShadow(vec4 shadowCoord) {
    return 1.0;
}

float MainLightShadow(vec4 shadowCoord, vec3 positionWS, vec4 shadowMask, vec4 occlusionProbes)
{
    return MainLightRealtimeShadow(shadowCoord);
}

Light GetMainLight(vec4 shadowCoord, vec3 positionWS, vec4 shadowMask)
{
    Light light = GetMainLight();
    light.shadowAttenuation = MainLightShadow(shadowCoord, positionWS, shadowMask, _MainLightOcclusionProbes);
    return light;
}

vec3 SafeNormalize(vec3 inVec)
{
    float dp3 = max(1.175494351e-38, dot(inVec, inVec));
    return inVec * rsqrt(dp3);
}

// 真源把 RMO 拆开、把主光与半程向量备好。家族的 <c>_RMOSMap</c> 那条路这一作用不上
// (材质里没有 <c>_UseRMOSMap</c> 也没有那张图),所以粗糙度/金属度/遮蔽/高光级在这里从
// <c>_RMOTex</c> 直接落。
void GirlsFrontline_Setup(inout RuriData ruriData, CharaVaryings input_)
{
    ruriData.mainLight = GetMainLight(ruriData.shadowCoord, ruriData.positionWS, ruriData.shadowMask);
    ruriData.V = ruriData.viewDirectionWS;
    ruriData.L = ruriData.mainLight.direction;
    ruriData.H = SafeNormalize(ruriData.L + ruriData.V);
    ruriData.useRampVal = (_UseRampMap ? 1.0 : 0.0);
    // 真源 b2593 第 126-129 行:`if (baseMap.a * _BaseColor.a - _Cutoff < 0) discard;`。
    // 家族的裁剪走的是它自己的 `_AlphaClip` / `_AlphaClipThreshold` 两条,而且只在非前向趟里跑;
    // 这一作的裁剪是**前向趟自己的**,开关与阈值也是它自己的两条名字,所以落在这里。
    if (_UseAlphaTest)
    {
        clip(ruriData.alpha - _Cutoff);
    }
    vec4 rmo = texture(_RMOTex, input_.uv);
    ruriData.roughness = rmo.x;
    ruriData.metallic = rmo.y;
    ruriData.occlusion = rmo.z;
    ruriData.specular = rmo.w;
}

// 真源 b2603 第 163-245 行 —— 脸部 SDF。
// 光向先进**物体空间**(真源 <c>mul(unity_WorldToObject, L)</c>;这里用 <c>UNITY_MATRIX_M</c> 的三列
// 点乘,对刚体+等比缩放是同一件事,而这两个宿主真正供得出的是 M 不是它的逆),取 xz 归一化;
// <c>_FaceLightDirAdjustment</c> 把这个二维方向往 (0,1) 掰。
// 两次采样 <c>_BlendTex.r</c>:原 uv 一次、u 镜像一次;<c>1 - _BlendTex.a &gt; 0.5</c> 决定
// 哪一份当近侧、哪一份当远侧,以及门限落在 [0,1) 还是 [1,2)。门限再按 x 的正负翻到 2 - t。
// 过渡带是**环绕**比较(真源用 <c>frac((t ± s/2 + 4) * 0.5) * 2</c> 把值折回 [0,2)):
// t + 4 恒为正,所以真源里那两个正负分支恒取正的那一支,这里直接写成折回式。
float GirlsFrontline_FaceShadow(vec2 faceUV, vec3 lightDirectionWS, out float faceUpFade)
{
    vec3 objectLight = ruriNormalize(half3(dot(lightDirectionWS, UNITY_MATRIX_M[0].xyz), dot(lightDirectionWS, UNITY_MATRIX_M[1].xyz), dot(lightDirectionWS, UNITY_MATRIX_M[2].xyz)));
    faceUpFade = 1.0 - abs(objectLight.z);
    vec2 lightXZ = ruriNormalize(half2(objectLight.x, objectLight.z));
    if (_FaceLightDirAdjustment > 0.0)
    {
        lightXZ = ruriNormalize(half2(lightXZ.x + _FaceLightDirAdjustment * (0.0 - lightXZ.x), lightXZ.y + _FaceLightDirAdjustment * (1.0 - lightXZ.y)));
    }
    vec4 nearSample = texture(_BlendTex, faceUV);
    float mirrored = texture(_BlendTex, half2(1.0 - faceUV.x, faceUV.y)).x;
    bool frontHalf = (1.0 - nearSample.w) > 0.5;
    float nearSide = (frontHalf ? nearSample.x : mirrored);
    float farSide = (frontHalf ? mirrored : nearSample.x);
    float rawThreshold = (frontHalf ? (lightXZ.y * 0.5 + 0.5) : (lightXZ.y * 0.5 + 1.5));
    float threshold = ((lightXZ.x < 0.0) ? (2.0 - rawThreshold) : rawThreshold);
    float smoothness = _BlendSmoothness;
    float lower = frac((threshold - smoothness * 0.5 + 4.0) * 0.5) * 2.0;
    float upper = frac((threshold + smoothness * 0.5 + 4.0) * 0.5) * 2.0;
    float wrapped = 1.0 - saturate(((2.0 - lower) - nearSide) / smoothness);
    float lowerTerm = ((lower < 1.0) ? saturate((farSide - lower) / smoothness) : wrapped);
    float upperTerm = 1.0 - saturate((upper - farSide) / smoothness);
    return ((upper < 1.0) ? min(upperTerm, lowerTerm) : max(wrapped, lowerTerm));
}

vec3 CalcDiffuseGirlsFrontline2(vec3 lightColor, vec3 distanceAtten, float NoL, float shadowAtten, float useRampMap)
{
    float atten = NoL * shadowAtten * distanceAtten.x;
    if (useRampMap <= 0.001)
        return atten * lightColor;
    // 真源的下限是 6.103515625e-05(= 2^-14,half 的最小正规数),不是 1e-4:
    // 斜坡那一格恰好落在这两个数之间时,取哪个决定的是「按斜坡首色平涂」还是「按 atten 线性收」。
    float rampY = 0.125;
    vec2 rampUV = half2(atten, rampY);
    rampUV.x = max(rampUV.x, 6.103515625e-05);
    vec3 ramp = textureLod(_RampMap, rampUV, 0).rgb;
    vec3 finalAtten = (rampUV.x > 6.103515625e-05 ? (ramp * min(rcp(rampUV.x) * atten, 1.0)) : ramp);
    return finalAtten * lightColor;
}

// 真源 b2603 第 288-306 行 —— 脸部高光。
// 取的是**相机前向**在物体空间的 xz(真源 <c>unity_CameraToWorld</c> 的第三列,寄存器 c1320,
// 由同安装别的着色器按名声明坐实),与光向的二维 xz 按 0.85 混合后决定采哪半边与阈值。
// 阈值式 <c>saturate(-dir.y - 0.70710677) * 3.4142134</c> 是真源逐字(√2/2 与 1+√2)。
// 形状由 <c>_BlendTex</c> 的 g/b 双阈值取交,再乘 N·V、<c>_Anisotropy</c>、1/π、
// <c>saturate(2 * lightXZ.y - 1)</c>(真源写成 <c>saturate(halfDir * 4 - 3)</c>,同一条)、
// SDF 阴影,最后是 <c>0.1 + 0.9 * N·L</c>。
float GirlsFrontline_FaceSpecular(vec2 faceUV, vec2 lightXZ, vec3 viewDirectionWS, float NoV, float NoL, float faceShadow)
{
    vec3 cameraForwardWS = -UNITY_MATRIX_I_V[2].xyz;
    vec3 objectForward = ruriNormalize(half3(dot(cameraForwardWS, UNITY_MATRIX_M[0].xyz), dot(cameraForwardWS, UNITY_MATRIX_M[1].xyz), dot(cameraForwardWS, UNITY_MATRIX_M[2].xyz)));
    vec2 steered = ruriNormalize(half2(lightXZ.x + (objectForward.x - lightXZ.x) * 0.85, lightXZ.y + (objectForward.z - lightXZ.y) * 0.85));
    vec2 shapeUV = half2((steered.x < 0.0 ? (1.0 - faceUV.x) : faceUV.x), faceUV.y - viewDirectionWS.y * _AnisotropyShift);
    vec3 shape = texture(_BlendTex, shapeUV).xyz;
    float threshold = clamp(saturate(-steered.y - 0.70710677) * 3.4142134, 0.01, 0.99);
    float band = ((shape.y >= (1.0 - threshold) ? 1.0 : 0.0)) * ((shape.z >= threshold ? 1.0 : 0.0));
    float intensity = NoV * band * _Anisotropy * INV_PI;
    intensity *= saturate((lightXZ.y * 0.5 + 0.5) * 4.0 - 3.0);
    intensity *= faceShadow;
    return intensity * 0.1 + (intensity * NoL) * 0.9;
}

vec3 SampleSH(vec3 normalWS) {
    return envIrradiance({Normal});
}

vec3 DecodeHDREnvironment(vec4 encodedIrradiance, vec4 decodeInstructions)
{
    float alpha = max(decodeInstructions.w * (encodedIrradiance.w - 1.0) + 1.0, 0.0);
    return (decodeInstructions.x * pow(alpha, decodeInstructions.y)) * encodedIrradiance.xyz;
}

vec2 CalcEnvBRDFApprox(float Roughness, float NoV)
{
    vec4 c0 = half4(-1, -0.0275, -0.572, 0.022);
    vec4 c1 = half4(1, 0.0425, 1.04, -0.04);
    vec4 r = Roughness * c0 + c1;
    float a004 = min(r.x * r.x, exp2(-9.28 * NoV)) * r.x + r.y;
    vec2 AB = half2(-1.04, 1.04) * a004 + r.zw;
    return AB;
}

vec3 CalcEnvBRDFGirlsFrontline2(vec3 specularColor, float roughness, float NoV_Clamp, vec3 normalWS, float useRampMap)
{
    vec2 AB = CalcEnvBRDFApprox(roughness, NoV_Clamp);
    if (useRampMap > 0.001)
    {
        // 真源读的是 $Globals 的 c1337(unity_MatrixV)与 c1341(unity_MatrixInvV)——
        // 同一安装别的着色器把这两处按名声明了出来,所以这两个身份是读出来的。
        // 这里改用 UNITY_MATRIX_V / UNITY_MATRIX_I_V:它们是同一对矩阵,而**两个宿主真正供得出的是它们**
        // (小写那对在配方的引擎态里没有落点,发出去就是一个恒 0 的 uniform,整条分支静默变常数)。
        vec3 vsRightDir = half3(UNITY_MATRIX_V[0].x, UNITY_MATRIX_V[1].x, UNITY_MATRIX_V[2].x);
        float rightSign = dot(vsRightDir, _MainLightPosition.xyz);
        float facingSign = (rightSign < 0.0 ? -1.0 : 1.0);
        vec3 rightDirWS = ruriNormalize(half3(facingSign, facingSign, facingSign) * float3(UNITY_MATRIX_I_V[0].x, UNITY_MATRIX_I_V[0].y, UNITY_MATRIX_I_V[0].z));
        float NDotRDWS_Clamp = saturate(dot(normalWS, rightDirWS));
        vec2 rampUV = half2(AB.y * NDotRDWS_Clamp, 0.625);
        AB.y = textureLod(_RampMap, rampUV, 0.0).x;
    }
    return specularColor * AB.x + AB.y;
}

// 真源 b2592 第 219-222 行:反射探针按 <c>roughness * 6</c> 取 mip,环境 BRDF 走
// <c>specularColor * AB.x + AB.y</c>(AB = Karis 的移动端近似,<see cref="CalcEnvBRDFApprox"/> 逐字同式)。
// 各向异性与脸那两支没有 RMO,真源在那里把粗糙度恒定成 1、金属度恒定成 0,
// 编译器于是把 <c>0.04 * AB.x(1)</c> 折成了常数 0.018096 —— 这里不抄那个折叠值,
// 照原式传 (0.04, 1) 让它自己算出同一个数。
vec3 GirlsFrontline_EnvironmentSpecular(vec3 specularColor, float roughness, float NoV, vec3 normalWS, vec3 viewDirectionWS, float useRampMap)
{
    vec3 reflectDirection = reflect(-viewDirectionWS, normalWS);
    vec4 encodedIrradiance = vec4(envSampleLOD(reflectDirection, roughness * 6.0), 1.0);
    vec3 probeColor = DecodeHDREnvironment(encodedIrradiance, unity_SpecCube0_HDR);
    return probeColor * CalcEnvBRDFGirlsFrontline2(specularColor, roughness, NoV, normalWS, useRampMap);
}

// 真源 b2603(<c>_USE_BLEND_TEX</c>)。这一支没有 RMO、没有法线图、没有自发光:
// 反编译件的纹理表就只有 <c>_BaseMap</c> / <c>_BlendTex</c> / <c>_RampMap</c> 三张,
// 与安装里那两张脸材质真绑的三张逐一对上。
void GirlsFrontline_Face(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    vec2 faceUV = (_UseSpecularUV2 ? input_.uv1.xy : input_.uv);
    vec3 objectLight = ruriNormalize(half3(dot(ruriData.L, UNITY_MATRIX_M[0].xyz), dot(ruriData.L, UNITY_MATRIX_M[1].xyz), dot(ruriData.L, UNITY_MATRIX_M[2].xyz)));
    vec2 lightXZ = ruriNormalize(half2(objectLight.x, objectLight.z));
    float faceUpFade;
    float faceShadow = GirlsFrontline_FaceShadow(faceUV, ruriData.L, faceUpFade);
    float shaded = (faceUpFade * 0.5 + 0.5) * faceShadow;
    vec3 diffuseColor = CalcDiffuseGirlsFrontline2(ruriData.mainLight.color, vec3(ruriData.mainLight.distanceAttenuation), shaded, ruriData.mainLight.shadowAttenuation, ruriData.useRampVal);
    float NoV = saturate(dot(ruriData.V, ruriData.normalWS));
    float NoL = max(dot(ruriData.normalWS, ruriData.L), 0.0);
    float specular = GirlsFrontline_FaceSpecular(faceUV, lightXZ, ruriData.V, NoV, NoL, faceShadow);
    vec3 ambient = max(SampleSH(ruriData.normalWS), 0.0);
    vec3 finalColor = (diffuseColor + specular) * ruriData.albedo + ambient * ruriData.albedo + GirlsFrontline_EnvironmentSpecular(half3(0.04, 0.04, 0.04), 1.0, NoV, ruriData.normalWS, ruriData.V, ruriData.useRampVal);
    finalColor *= _FinalTint.xyz;
    outputData.baseColor = ruriData.albedo;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(finalColor, ruriData.alpha);
}

// 真源 <c>gf_shader/pbr/character/eye</c> 的 b288。
// 两张图各走自己的视差位移,底色不乘 <c>_BaseColor</c>(那份变体里根本没引用),
// 漫反射是 <c>lerp(_ShadowIntensity, 1, N·L)</c>,高光是 <c>N·L * _Specularmap * _SpecularIntensity</c>,
// 出射 alpha 恒 0。视差量是顶点腿算的一维偏移:物体空间视线的 z × 顶点色 g × 切线手性
// × <c>unity_WorldTransformParams.w</c>。
void GirlsFrontline_Eyes(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    vec3 objectView = ruriNormalize(half3(dot(ruriData.V, UNITY_MATRIX_M[0].xyz), dot(ruriData.V, UNITY_MATRIX_M[1].xyz), dot(ruriData.V, UNITY_MATRIX_M[2].xyz)));
    float parallax = objectView.z * input_.color.y * input_.tangentWS.w * unity_WorldTransformParams.w;
    vec3 baseColor = ruriSampleSrgb(_MainTex, ruriUvClamp(_MainTex, half2(input_.uv.x + parallax * _CorneaParallax, input_.uv.y))).xyz;
    vec3 specularMap = ruriSampleSrgb(_Specularmap, half2(input_.uv.x + parallax * _SpecularParallax, input_.uv.y)).xyz;
    float NoL = saturate(dot(ruriData.normalWS, ruriData.L));
    vec3 lightColor = ruriData.mainLight.color;
    vec3 specular = specularMap * _SpecularIntensity * NoL;
    vec3 diffuse = baseColor * lightColor * lerp(_ShadowIntensity, 1.0, NoL);
    vec3 ambient = max(SampleSH(ruriData.normalWS), 0.0);
    vec3 finalColor = diffuse + specular * lightColor + ambient * baseColor;
    finalColor *= _FinalTint.xyz;
    outputData.baseColor = baseColor;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(finalColor, 0.0);
}

// 真源 <c>…/eyeblend_add</c> 的 b48(<c>Blend One One</c>):
// <c>rgb = _MainTex.rgb * _MainColor.rgb * _SpecularIntensity * (saturate(N·L) * 0.8 + 0.2)</c>、
// <c>a = _MainTex.a * _MainColor.a</c>。整份着色器就这一段,没有别的。
void GirlsFrontline_EyeBlendAdd(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    vec4 mask = ruriSampleSrgb(_MainTex, ruriUvClamp(_MainTex, input_.uv));
    float lightTerm = saturate(dot(ruriData.normalWS, ruriData.L)) * 0.8 + 0.2;
    vec3 finalColor = mask.xyz * _MainColor.xyz * _SpecularIntensity * lightTerm;
    outputData.baseColor = mask.xyz;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(finalColor, mask.w * _MainColor.w);
}

// 真源 <c>…/eyeblend_multiply</c> 的 b16(<c>Blend DstColor Zero</c>):
// <c>rgb = 1 + _SpecularIntensity * (_MainTex.rgb * _MainColor.rgb - 1)</c>,
// 也就是把「乘进帧缓冲的因子」直接写出来 —— 所以这个部位的 <c>[StylePart]</c> 标了
// <c>MultiplyBlend</c>,over 混合的宿主据此自己做等价分解。
void GirlsFrontline_EyeBlendMultiply(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    vec4 mask = ruriSampleSrgb(_MainTex, ruriUvClamp(_MainTex, input_.uv));
    vec3 factor = 1.0 + _SpecularIntensity * (mask.xyz * _MainColor.xyz - 1.0);
    outputData.baseColor = mask.xyz;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(factor, 1.0);
}

// 真源 b2602 第 235-252 行(各向异性高光带)。
// 带的形状是 <c>_BlendTex</c> 在**沿 v 推过**的 uv 上的 rgb,乘 N·V 与 <c>_Anisotropy</c>;
// 出射 = <c>带 * 0.1/π + (N·L 遮罩 * 带) * 0.9/π</c>。
// 两个系数在反编译件里是 0.031830988824367523 与 0.28647887706756592,即 <c>INV_PI * 0.1</c> 与
// <c>INV_PI * 0.9</c>,不是手调的魔数。
vec3 GirlsFrontline_AnisotropicBand(vec2 anisotropyUV, float NoV, float maskedNoL)
{
    vec3 band = texture(_BlendTex, anisotropyUV).xyz * (NoV * _Anisotropy);
    return band * (INV_PI * 0.1) + (band * maskedNoL) * (INV_PI * 0.9);
}

// 真源 b2602(<c>_ANISOTROPIC_SPECULAR</c>)—— 头发那一支。
// 这支**没有** RMO、没有自发光、没有 PBR 高光:真源把粗糙度恒定在 1、金属度恒定在 0,
// 反射探针固定取 mip 6,直接光只有「斜坡漫反射 + 各向异性带」。
void GirlsFrontline_Anisotropic(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    vec4 blend = texture(_BlendTex, input_.uv);
    float maskedNoL = max(dot(ruriData.normalWS, ruriData.L), 0.0) * blend.w;
    vec3 diffuseColor = CalcDiffuseGirlsFrontline2(ruriData.mainLight.color, vec3(ruriData.mainLight.distanceAttenuation), maskedNoL, ruriData.mainLight.shadowAttenuation, ruriData.useRampVal);
    vec2 anisotropyUV = (_UseSpecularUV2 ? input_.uv1.xy : input_.uv);
    anisotropyUV.y -= ruriData.V.y * _AnisotropyShift;
    float NoV = saturate(dot(ruriData.V, ruriData.normalWS));
    vec3 band = GirlsFrontline_AnisotropicBand(anisotropyUV, NoV, maskedNoL);
    vec3 ambient = max(SampleSH(ruriData.normalWS), 0.0);
    vec3 finalColor = diffuseColor * ruriData.albedo + band * ruriData.mainLight.color * ruriData.mainLight.distanceAttenuation + ambient * ruriData.albedo + GirlsFrontline_EnvironmentSpecular(half3(0.04, 0.04, 0.04), 1.0, NoV, ruriData.normalWS, ruriData.V, ruriData.useRampVal);
    finalColor *= _FinalTint.xyz;
    outputData.baseColor = ruriData.albedo;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(finalColor, ruriData.alpha);
}

float D_GGX_Anisotropic(float TdotH, float BdotH, float NdotH, float alpha_t, float alpha_b)
{
    float a2 = alpha_t * alpha_b;
    vec3 v = float3(TdotH * alpha_b, BdotH * alpha_t, NdotH * a2);
    float v2 = dot(v, v);
    float w2 = ((v2 != a2) ? a2 / v2 : 1.0);
    return min(a2 * w2 * w2 * INV_PI, 2048.0);
}

float D_GGX_Float(float NdotH, float alpha2)
{
    float d = (NdotH * alpha2 - NdotH) * NdotH + 1.0;
    float d2 = d * d;
    float D = ((d2 != alpha2) ? alpha2 / d2 : 1.0);
    return min(D, 2048.0);
}

float V_SmithGGX_Hammon(float roughness, float NoV, float NoL)
{
    float a = roughness * roughness;
    float Vis_V = NoL * (NoV * (1.0 - a) + a);
    float Vis_L = NoV * (NoL * (1.0 - a) + a);
    return min(0.5 * rcp(Vis_V + Vis_L), 1.0);
}

float Pow5(float x)
{
    float x2 = x * x;
    return x2 * x2 * x;
}

vec3 CalcFresnelSchlickGirlsFrontline2(vec3 specularColor, float VoH_Clamp)
{
    float Fc = Pow5(max(1 - VoH_Clamp, 0.001));
    return vec3(saturate(50.0 * specularColor.g) * Fc + (1 - Fc));
}

vec3 CalcSpecularGirlsFrontline2(vec3 specularColor, float roughness, vec3 N, vec3 tangentWS, vec3 bitangentDirWS, vec3 halfDir, float NoH, float NoV, float NoL, float VoH, float LoH, float anisotropicGGX, float useRampMap)
{
    float NoH_Safe = saturate(NoH);
    float NoV_Safe = max(NoV, 1e-4);
    float NoL_Safe = max(NoL, 1e-4);
    float VoH_Safe = max(VoH, 1e-4);
    float LoH_Safe = max(LoH, 1e-4);
    // 真源的各向同性 D 是 Filament 那一式:a = 粗糙度², k = a / (1 - NoH² + (NoH·a)²), D = k²。
    // 本仓的 D_GGX_Float(NoH, alpha2) 算的是 alpha2 / (NoH²(alpha2-1)+1)²,两式在 alpha2 = a² 时
    // 逐字相等 —— 所以传进去的是**四次方**。传二次方(上一版)等于把 α 开了一次根号,高光宽一圈。
    float alpha = roughness * roughness;
    float D = 0;
    if (abs(anisotropicGGX) > 0.001)
    {
        float TdotH = dot(tangentWS, halfDir);
        float BdotH = dot(bitangentDirWS, halfDir);
        float roughnessT = max(alpha * (1.0 + anisotropicGGX), 0.001);
        float roughnessB = max(alpha * (1.0 - anisotropicGGX), 0.001);
        D = D_GGX_Anisotropic(TdotH, BdotH, NoH_Safe, roughnessT, roughnessB);
    }
    else
    {
        D = D_GGX_Float(NoH_Safe, alpha * alpha);
    }
    float V = V_SmithGGX_Hammon(roughness, NoV_Safe, NoL_Safe);
    float Fc = CalcFresnelSchlickGirlsFrontline2(specularColor, VoH_Safe).x;
    // 真源把 D·V·F 这一整段先 clamp 到 [0, 10] 再乘高光色(反编译件逐字 clamp(x, 0, 10)):
    // 掠射角上 D 能冲到 2048 的上限,不夹住就是一圈过曝白边。
    if (useRampMap > 0.001)
    {
        float D2 = D_GGX_Float(1.0, alpha * alpha);
        float V2 = V_SmithGGX_Hammon(roughness, VoH_Safe, LoH_Safe);
        float den = max(D2 * V2, 1e-4);
        vec2 rampUV;
        rampUV.x = saturate(D * V / den);
        rampUV.y = 0.375;
        vec3 ramp = textureLod(_RampMap, rampUV, 0.0).rgb;
        return clamp(ramp * (D2 * V2 * Fc), 0.0, 10.0) * specularColor;
    }
    return clamp(half3(D * V * Fc, D * V * Fc, D * V * Fc), 0.0, 10.0) * specularColor;
}

vec3 CharaVaryings_GetBitangentWS(CharaVaryings ruriSelf)
{
    return ruriSelf.tangentWS.w * cross(ruriSelf.normalWS.xyz, ruriSelf.tangentWS.xyz);
}

// 真源 b2592(全关的兜底变体)+ b2594(<c>_USE_STOCKING</c>)。
// 直接光 = <c>(漫反射色 + 高光BRDF) × 斜坡衰减 × 主光色</c>;
// 间接漫反射 = <c>漫反射色 × SH × 遮蔽</c>;间接高光 = 反射探针 × 环境 BRDF(**不乘遮蔽**,真源如此);
// 自发光 = <c>反照率 × _EmissiveIntensity × RMO.a</c>,而 b2594 里各向异性 GGX 开着时这一项被整条丢掉。
// 高光 BRDF 的 D 项:真源是 Filament 的 <c>k = α/(1 - NoH² + (NoH·α)²), D = k²</c>,α = 粗糙度²;
// 本仓的 <see cref="D_GGX_Float"/> 写成 <c>alpha2/(NoH²(alpha2-1)+1)²</c>,两式在
// <c>alpha2 = α²</c> 时逐字相等 —— 所以这里传的是**粗糙度的四次方**,不是二次方。
// (传二次方是上一版的偏差:同一条式子少平方一次,高光会宽一圈。)
void GirlsFrontline_Body(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    if (_AnisotropicSpecular)
    {
        GirlsFrontline_Anisotropic(ruriData, input_, outputData);
        return;
    }
    vec3 normalWS = ruriData.normalWS;
    float NoL = max(dot(normalWS, ruriData.L), 0.0);
    float NoH = max(dot(normalWS, ruriData.H), 0.0);
    float VoH = max(dot(ruriData.V, ruriData.H), 0.0);
    float LoH = max(dot(ruriData.L, ruriData.H), 0.0);
    float NoV = min(max(dot(normalWS, ruriData.V), 0.0) + 1e-5, 1.0);
    vec3 diffuseColor = ruriData.albedo * (1.0 - ruriData.metallic);
    vec3 specularColor;
    float emissionGate = 1.0;
    if (_UseStockingFalloff)
    {
        float stockingLevel = ((abs(_AnisotropicGXX) > 0.001 ? ruriData.specular : 0.5)) * 0.08;
        specularColor = stockingLevel + (ruriData.albedo - stockingLevel) * ruriData.metallic;
        vec3 falloff = lerp(_StockingFalloffColor.xyz, _StockingCenterColor.xyz, pow(max(NoV, 1e-4), _StockingFalloffPower));
        diffuseColor *= falloff;
        emissionGate = (abs(_AnisotropicGXX) > 0.001 ? 0.0 : 1.0);
    }
    else
    {
        specularColor = lerp(half3(0.04, 0.04, 0.04), ruriData.albedo, ruriData.metallic);
    }
    vec3 attenuation = CalcDiffuseGirlsFrontline2(ruriData.mainLight.color, vec3(ruriData.mainLight.distanceAttenuation), NoL, ruriData.mainLight.shadowAttenuation, ruriData.useRampVal);
    vec3 specularBRDF = CalcSpecularGirlsFrontline2(specularColor, ruriData.roughness, normalWS, input_.tangentWS.xyz, CharaVaryings_GetBitangentWS(input_), ruriData.H, NoH, NoV, NoL, VoH, LoH, _AnisotropicGXX, ruriData.useRampVal);
    vec3 ambient = max(SampleSH(normalWS), 0.0);
    vec3 emission = ruriData.albedo * _EmissiveIntensity * ruriData.specular * emissionGate;
    vec3 finalColor = (diffuseColor + specularBRDF) * attenuation + ambient * diffuseColor * ruriData.occlusion + GirlsFrontline_EnvironmentSpecular(specularColor, ruriData.roughness, NoV, normalWS, ruriData.V, ruriData.useRampVal) + emission;
    finalColor *= _FinalTint.xyz;
    outputData.baseColor = ruriData.albedo;
    outputData.roughness = ruriData.roughness;
    outputData.metallic = ruriData.metallic;
    outputData.specular = ruriData.specular;
    outputData.normalWS = ruriData.normalWS;
    outputData.globalIllumination = half4(finalColor, ruriData.alpha);
}

// 部位 = 材质指着哪份着色器(<c>ShaderName</c>),不是属性指纹。
// · <c>uber</c> 与 <c>ubertrans</c> 是**同一个表面**:两份反编译件的片元尾段
// (自发光 + 环境高光 + 直接光 + 间接漫反射 → <c>_FinalTint</c> → 选中描色)逐项同构,
// 差别全在 pass 状态与写出的 alpha(不透明恒 1 / 半透明写底色 alpha),
// 所以收成 <c>Aliases</c> 而不是再开一个部位(一个部位 = 一棵树,多开一份就是同一表面的第二真源)。
// · 脸与身体共用 <c>uber</c>,靠 <c>_UseBlendTex</c> 区分 —— 那条开关在这个参考角色的
// 12 份 uber 材质里只有 2 份为 1,正是两份脸材质,且它们绑的三张图与脸那份变体的纹理表逐一对上。
// · 眼睛三份各是自己的着色器、自己的混合,分成三个部位。
void Fragment_GirlsFrontline(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData)
{
    GirlsFrontline_Setup(ruriData, input_);
    int partId = _CharaPartID;
    if (partId == 1)
        GirlsFrontline_Face(ruriData, input_, outputData);
    else
        if (partId == 2)
            GirlsFrontline_Eyes(ruriData, input_, outputData);
        else
            if (partId == 3)
                GirlsFrontline_EyeBlendAdd(ruriData, input_, outputData);
            else
                if (partId == 4)
                    GirlsFrontline_EyeBlendMultiply(ruriData, input_, outputData);
                else
                    GirlsFrontline_Body(ruriData, input_, outputData);
}

void CalcRuriNPR(inout RuriData ruriData, CharaVaryings input_, inout RuriGBufferData outputData, float facing)
{
    Fragment_GirlsFrontline(ruriData, input_, outputData);
}

vec3 RuriCharaAdditionalLights(vec3 positionWS, vec3 N, vec2 normalizedScreenSpaceUV, vec3 albedo)
{
    vec3 lightAccum = float3(0.0, 0.0, 0.0);
    return lightAccum;
}

vec3 PackGBufferNormal(vec3 normalWS)
{
    float l1 = abs(normalWS.x) + abs(normalWS.y) + abs(normalWS.z);
    float inv = 1.0 / ((l1 > 1e-6 ? l1 : 1e-6));
    vec3 n = normalWS * inv;
    float t = saturate(-n.z);
    vec2 oct = float2(n.x + ((n.x >= 0.0 ? t : -t)), n.y + ((n.y >= 0.0 ? t : -t)));
    vec2 remapped = saturate(float2(oct.x * 0.5 + 0.5, oct.y * 0.5 + 0.5));
    uint2 i = uint2(uint((remapped.x * 4095.5)), uint((remapped.y * 4095.5)));
    uint2 hi = uint2(i.x >> 8, i.y >> 8);
    uint2 lo = uint2(i.x & 255, i.y & 255);
    return float3(lo.x / 255.0, lo.y / 255.0, (hi.x | (hi.y << 4)) / 255.0);
}

GBufferFragOutput RuriGBufferDataToCharaGbuffer(RuriData ruriData, RuriGBufferData outputData)
{
    vec3 packedNormalWS = PackGBufferNormal(outputData.normalWS);
    GBufferFragOutput output_ = ruriZeroGBufferFragOutput();
    float unused = 0;
    output_.gBuffer0 = float4(outputData.baseColor, outputData.alpha);
    output_.gBuffer1 = float4(unused, outputData.metallic, outputData.specular, outputData.occlusion);
    output_.gBuffer2 = float4(packedNormalWS, 1.0 - outputData.roughness);
    output_.color = vec4(outputData.globalIllumination);
    return output_;
}

GBufferFragOutput CharaMixedPassFragment(CharaVaryings input_, float facing)
{
    RuriData ruriData;
    InitializeCharaData(input_, ruriData);
    GBufferData gBufferData = ruriSelfGBuffer(ruriData);
    if (_SurfaceType != 1)
    {
        ruriData.albedo = gBufferData.baseColor;
    }
    ruriData.albedo *= _BaseColor.rgb;
    ruriData.alpha *= _BaseColor.a;
    if (!_UseRMOSMap)
    {
        ruriData.roughness = _RoughnessIntensity;
        ruriData.metallic = _MetallicIntensity;
        ruriData.occlusion = 1.0;
        ruriData.specular = _SpecularIntensity;
    }
    RuriGBufferData outputData = ruriZeroRuriGBufferData();
    CalcRuriNPR(ruriData, input_, outputData, facing);
    outputData.baseColor = outputData.globalIllumination.xyz;
    outputData.baseColor.rgb = outputData.baseColor.rgb + RuriCharaAdditionalLights(ruriData.positionWS, ruriData.normalWS, ruriData.normalizedScreenSpaceUV, ruriData.albedo);
    outputData.alpha = ruriData.alpha;
    return RuriGBufferDataToCharaGbuffer(ruriData, outputData);
}

//----------------------------------------------------------------------region Shader 入口
void shade(V2F inputs) {
    ruriSparseCoord = inputs.sparse_coord;
    CharaVaryings ruriInput = ruriZeroCharaVaryings();
    ruriInput.uv = inputs.sparse_coord.tex_coord;
    ruriInput.positionWS = inputs.position;
    ruriInput.normalWS = normalize(inputs.normal);
    ruriInput.tangentWS = float4(normalize(inputs.tangent), (dot(cross(normalize(inputs.normal), normalize(inputs.tangent)), normalize(inputs.bitangent)) < 0.0) ? -1.0 : 1.0);
    ruriInput.uv1 = float4(0.0, 0.0, 0.0, 0.0);
    ruriInput.uv0zw = float2(0.0, 0.0);
    ruriInput.positionNDC = float4(0.0, 0.0, 1.0, 1.0);
    ruriInput.color = float4(1.0, 1.0, 1.0, 1.0);
    ruriInput.positionCS = gl_FragCoord;
    GBufferFragOutput ruriOut = CharaMixedPassFragment(ruriInput, ((uniform_facing >= 0) ? 1.0 : -1.0));
    if (_CharaPartID == 4)
    {
        vec3 ruriFactor = clamp(ruriOut.gBuffer0.rgb, 0.0, 1.0);
        float ruriDarken = 1.0 - min(min(ruriFactor.r, ruriFactor.g), ruriFactor.b);
        vec3 ruriSrc = ruriDarken > 1e-5 ? (ruriFactor - (1.0 - ruriDarken)) / ruriDarken : vec3(0.0);
        alphaOutput(ruriDarken);
        diffuseShadingOutput(ruriSrc);
    }
    else
    {
        alphaOutput(ruriOut.gBuffer0.a);
        diffuseShadingOutput(ruriOut.gBuffer0.rgb);
    }
}
//----------------------------------------------------------------------endregion
