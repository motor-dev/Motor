/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_SHADER_SHADER_META_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_SHADER_SHADER_META_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {
namespace Shaders {

class Node;
class IShaderBuilder;
class Output;

enum Stage
{
    VertexStage,
    GeometryStage,
    TesselationControlStage,
    TessalationEvaluationStage,
    FragmentStage
};

}  // namespace Shaders

class motor_api(3D) ShaderProgramDescription
    : public Resource::Description< ShaderProgramDescription >
{
private:
    minitl::vector< ref< Shaders::Output > > m_outputs;

protected:
    explicit ShaderProgramDescription(minitl::vector< ref< Shaders::Output > > outputs);
    ~ShaderProgramDescription() override;

public:
    virtual void buildSource(Shaders::IShaderBuilder & builder) const;
};

}  // namespace Motor

#endif
