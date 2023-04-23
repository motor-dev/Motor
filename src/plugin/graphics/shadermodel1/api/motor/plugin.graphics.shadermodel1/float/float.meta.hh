/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.shadermodel1/stdafx.h>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>

namespace Motor { namespace Float { namespace Float {

class Constant : public Shaders::Float
{
    published : const float value;
    published : explicit Constant(float value);
    ~Constant() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

class Uniform : public Shaders::Float
{
    published : const istring name;
    published : explicit Uniform(istring name);
    ~Uniform() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

class Varying : public Shaders::Float
{
    published : Varying();
    ~Varying() override;

private:
    void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                           Shaders::Stage targetStage) const override;
    void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                          Shaders::Stage targetStage) const override;
};

}}}  // namespace Motor::Float::Float
