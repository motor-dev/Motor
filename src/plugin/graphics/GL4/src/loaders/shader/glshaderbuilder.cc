/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <loaders/shader/glshaderbuilder.hh>

namespace Motor { namespace OpenGL {

static const char* toString(Shaders::Semantic semantic)
{
    switch(semantic)
    {
    case Shaders::Position: return "gl_Position";
    case Shaders::Color: return "gl_FragColor";
    case Shaders::Depth: return "gl_FragDepth";
    default:
        motor_error_format(Log::gl(), "semantic {0} not recognized by the GLSL shader builder",
                           u32(semantic));
        return "gl_FragColor";
    }
}

static const char* toString(Shaders::ValueType type)
{
    switch(type)
    {
    case Shaders::Type_Float: return "float";
    case Shaders::Type_Float2: return "vec2";
    case Shaders::Type_Float3: return "vec3";
    case Shaders::Type_Float4: return "vec4";
    case Shaders::Type_Float2x2: return "mat2";
    case Shaders::Type_Float2x3: return "mat2x3";
    case Shaders::Type_Float2x4: return "mat2x4";
    case Shaders::Type_Float3x2: return "mat3x2";
    case Shaders::Type_Float3x3: return "mat3";
    case Shaders::Type_Float3x4: return "mat3x4";
    case Shaders::Type_Float4x2: return "mat4x2";
    case Shaders::Type_Float4x3: return "mat4x3";
    case Shaders::Type_Float4x4: return "mat4";
    case Shaders::Type_Double: return "double";
    case Shaders::Type_Double2: return "dvec2";
    case Shaders::Type_Double3: return "dvec3";
    case Shaders::Type_Double4: return "dvec4";
    case Shaders::Type_Double2x2: return "dmat2";
    case Shaders::Type_Double2x3: return "dmat2x3";
    case Shaders::Type_Double2x4: return "dmat2x4";
    case Shaders::Type_Double3x2: return "dmat3x2";
    case Shaders::Type_Double3x3: return "dmat3";
    case Shaders::Type_Double3x4: return "dmat3x4";
    case Shaders::Type_Double4x2: return "dmat4x2";
    case Shaders::Type_Double4x3: return "dmat4x3";
    case Shaders::Type_Double4x4: return "dmat4";
    case Shaders::Type_Int: return "int";
    case Shaders::Type_Int2: return "ivec2";
    case Shaders::Type_Int3: return "ivec3";
    case Shaders::Type_Int4: return "ivec4";
    case Shaders::Type_Uint: return "uint";
    case Shaders::Type_Uint2: return "uvec2";
    case Shaders::Type_Uint3: return "uvec3";
    case Shaders::Type_Uint4: return "uvec4";
    case Shaders::Type_Bool: return "bool";
    case Shaders::Type_Bool2: return "bvec2";
    case Shaders::Type_Bool3: return "bvec3";
    case Shaders::Type_Bool4: return "bvec4";
    default:
        motor_error_format(Log::gl(), "type {0} not recognized by the GLSL shader builder",
                           u32(type));
        return "mat4";
    }
}

GLShaderBuilder::GLShaderBuilder(GLenum shaderType) : m_shaderType(shaderType)
{
    writeln("#version 140");
    motor_forceuse(m_shaderType);
}

GLShaderBuilder::~GLShaderBuilder() = default;

void GLShaderBuilder::doAddUniformDeclaration(const istring&     name, Shaders::Stage /*stage*/,
                                              Shaders::ValueType type)
{
    writeln(minitl::format< 1024u >(FMT("uniform {0} {1};"), toString(type), name).c_str());
}

void GLShaderBuilder::doAddVaryingDeclaration(const istring& name, Shaders::Stage stage,
                                              Shaders::ValueType type)
{
    if(stage == Shaders::VertexStage)
    {
        writeln(minitl::format< 1024u >(FMT("out {0} {1};"), toString(type), name).c_str());
    }
    else
    {
        writeln(minitl::format< 1024u >(FMT("in {0} {1};"), toString(type), name).c_str());
    }
}

void GLShaderBuilder::doAddAttributeDeclaration(const istring& name, Shaders::Stage stage,
                                                Shaders::ValueType type)
{
    if(stage == Shaders::VertexStage)
    {
        writeln(minitl::format< 1024u >(FMT("in {0} {1};"), toString(type), name).c_str());
    }
    else if(stage == Shaders::FragmentStage)
    {
        motor_assert(false, "not yet");
    }
}

void GLShaderBuilder::doAddMethod(const istring& name)
{
    writeln("");
    writeln(minitl::format< 1024u >(FMT("void {0} ()"), name).c_str());
    writeln("{");
    indent();
}

void GLShaderBuilder::doEndMethod()
{
    unindent();
    writeln("}");
}

void GLShaderBuilder::doSaveTo(Shaders::Semantic semantic, const istring& value)
{
    writeln(minitl::format< 1024u >(FMT("{0} = {1};"), toString(semantic), value).c_str());
}

void GLShaderBuilder::doSaveTo(const istring& name, const istring& value)
{
    writeln(minitl::format< 1024u >(FMT("{0} = {1};"), name, value).c_str());
}

void GLShaderBuilder::doAddOperator(Shaders::Operator op, Shaders::ValueType type,
                                    const istring& result, const istring& op1, const istring& op2)
{
    writeln(minitl::format< 1024u >(FMT("{0} {1} = {2} {3} {4};"), toString(type), result, op1,
                                    (char)op, op2)
                .c_str());
}

void GLShaderBuilder::doWrite(float value)
{
    write(minitl::format< 1024u >(FMT("{0}"), value));
}

void GLShaderBuilder::doWrite(knl::float2 value)
{
    write(minitl::format< 1024u >(FMT("vec2({0}, {1})"), value._0, value._1));
}

void GLShaderBuilder::doWrite(knl::float3 value)
{
    write(minitl::format< 1024u >(FMT("vec3({0}, {1}, {2})"), value._0, value._1, value._2));
}

void GLShaderBuilder::doWrite(knl::float4 value)
{
    write(minitl::format< 1024u >(FMT("vec4({0}, {1}, {2}, {3})"), value._0, value._1, value._2,
                                  value._3));
}

void GLShaderBuilder::doWrite(int value)
{
    write(minitl::format< 1024u >(FMT("{0}"), value));
}

void GLShaderBuilder::doWrite(knl::int2 value)
{
    write(minitl::format< 1024u >(FMT("ivec2({0}, {1})"), value._0, value._1));
}

void GLShaderBuilder::doWrite(knl::int3 value)
{
    write(minitl::format< 1024u >(FMT("ivec3({0}, {1}, {2})"), value._0, value._1, value._2));
}

void GLShaderBuilder::doWrite(knl::int4 value)
{
    write(minitl::format< 1024u >(FMT("ivec4({0}, {1}, {2}, {3})"), value._0, value._1, value._2,
                                  value._3));
}

void GLShaderBuilder::doWrite(bool value)
{
    write(value ? "true" : "false");
}

}}  // namespace Motor::OpenGL
