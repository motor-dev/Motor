/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_SHADERMODEL1_FLOAT_FLOAT4_META_HH
#define MOTOR_PLUGIN_GRAPHICS_SHADERMODEL1_FLOAT_FLOAT4_META_HH

#include <motor/plugin.graphics.shadermodel1/stdafx.h>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>

namespace Motor { namespace Float { namespace Float4 {

class Constant : public Shaders::Float4
{
public:
    const knl::float4 value;

public:
    explicit Constant(knl::float4 value);
    ~Constant() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

class Uniform : public Shaders::Float4
{
public:
    const istring name;

public:
    explicit Uniform(istring name);
    ~Uniform() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

class Varying : public Shaders::Float4
{
public:
    Varying();
    ~Varying() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

}}}  // namespace Motor::Float::Float4

#endif
