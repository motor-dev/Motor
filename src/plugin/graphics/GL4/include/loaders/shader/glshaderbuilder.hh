/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_GL4_LOADERS_SHADER_GLSHADERBUILDER_HH
#define MOTOR_PLUGIN_GRAPHICS_GL4_LOADERS_SHADER_GLSHADERBUILDER_HH

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/shader/ishaderbuilder.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace OpenGL {

struct GLShaderBuilder : public Shaders::IShaderBuilder
{
private:
    GLenum m_shaderType;

public:
    explicit GLShaderBuilder(GLenum shaderType);
    ~GLShaderBuilder() override;

    istring attributes[64];

private:
    void doAddUniformDeclaration(const istring& name, Shaders::Stage stage,
                                 Shaders::ValueType type) override;
    void doAddVaryingDeclaration(const istring& name, Shaders::Stage stage,
                                 Shaders::ValueType type) override;
    void doAddAttributeDeclaration(const istring& name, Shaders::Stage stage,
                                   Shaders::ValueType type) override;
    void doAddOperator(Shaders::Operator op, Shaders::ValueType type, const istring& result,
                       const istring& op1, const istring& op2) override;
    void doAddMethod(const istring& name) override;
    void doEndMethod() override;
    void doWrite(float value) override;
    void doWrite(knl::float2 value) override;
    void doWrite(knl::float3 value) override;
    void doWrite(knl::float4 value) override;
    void doWrite(int value) override;
    void doWrite(knl::int2 value) override;
    void doWrite(knl::int3 value) override;
    void doWrite(knl::int4 value) override;
    void doWrite(bool value) override;
    void doSaveTo(Shaders::Semantic semantic, const istring& value) override;
    void doSaveTo(const istring& name, const istring& value) override;
};

}}  // namespace Motor::OpenGL

#endif
