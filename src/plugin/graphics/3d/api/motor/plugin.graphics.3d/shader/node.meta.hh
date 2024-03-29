/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_SHADER_NODE_META_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_SHADER_NODE_META_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/core/memory/streams.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace Shaders {

class IShaderBuilder;

class motor_api(3D) Node : public minitl::pointer
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

#include <motor/plugin.graphics.3d/shader/node.meta.factory.hh>
#endif
