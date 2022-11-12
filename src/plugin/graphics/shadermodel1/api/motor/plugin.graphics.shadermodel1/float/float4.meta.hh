/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.shadermodel1/stdafx.h>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>

namespace Motor { namespace Float { namespace Float4 {

class Constant : public Shaders::Float4
{
    published : const knl::float4 value;
    published : Constant(knl::float4 value);
    ~Constant();

private:
    virtual void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                   Shaders::Stage targetStage) const override;
    virtual void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                  Shaders::Stage targetStage) const override;
};

class Uniform : public Shaders::Float4
{
    published : const istring name;
    published : Uniform(istring name);
    ~Uniform();

private:
    virtual void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                   Shaders::Stage targetStage) const override;
    virtual void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                  Shaders::Stage targetStage) const override;
};

class Varying : public Shaders::Float4
{
    published : Varying();
    ~Varying();

private:
    virtual void buildDeclarations(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                   Shaders::Stage targetStage) const override;
    virtual void buildDefinitions(Shaders::IShaderBuilder& stream, Shaders::Stage currentStage,
                                  Shaders::Stage targetStage) const override;
};

}}}  // namespace Motor::Float::Float4
