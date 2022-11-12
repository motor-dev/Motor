/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.shadermodel1/stdafx.h>
#include <motor/plugin.graphics.3d/shader/ishaderbuilder.hh>
#include <motor/plugin.graphics.shadermodel1/float/float4.meta.hh>

namespace Motor { namespace Float { namespace Float4 {

Constant::Constant(knl::float4 value) : value(value)
{
}

Constant::~Constant()
{
}

void Constant::buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                 Shaders::Stage targetStage) const
{
    motor_forceuse(stream);
    motor_forceuse(currentStage);
    motor_forceuse(targetStage);
}

void Constant::buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage /*currentStage*/,
                                Shaders::Stage /*targetStage*/) const
{
    stream.write(value);
}

Varying::Varying()
{
}

Varying::~Varying()
{
}

void Varying::buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                Shaders::Stage targetStage) const
{
    motor_forceuse(stream);
    motor_forceuse(currentStage);
    motor_forceuse(targetStage);
}

void Varying::buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                               Shaders::Stage targetStage) const
{
    motor_forceuse(stream);
    motor_forceuse(currentStage);
    motor_forceuse(targetStage);
}

Uniform::Uniform(istring name) : name(name)
{
}

Uniform::~Uniform()
{
}

void Uniform::buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                Shaders::Stage targetStage) const
{
    motor_forceuse(stream);
    motor_forceuse(currentStage);
    motor_forceuse(targetStage);
}

void Uniform::buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                               Shaders::Stage targetStage) const
{
    motor_forceuse(stream);
    motor_forceuse(currentStage);
    motor_forceuse(targetStage);
}

}}}  // namespace Motor::Float::Float4
