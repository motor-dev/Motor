/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/core/memory/streams.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace Shaders {

class IShaderBuilder;

class motor_api(3D) Node : public minitl::refcountable
{
protected:
    Node();
    ~Node() override;

public:
    virtual void buildDeclarations(IShaderBuilder & stream, Stage currentStage, Stage targetStage)
        const
        = 0;
    virtual void buildDefinitions(IShaderBuilder & stream, Stage currentStage, Stage targetStage)
        const
        = 0;
};

}}  // namespace Motor::Shaders
