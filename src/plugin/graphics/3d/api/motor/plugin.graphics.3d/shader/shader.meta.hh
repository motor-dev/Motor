/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_SHADER_SHADER_META_HH_
#define MOTOR_3D_SHADER_SHADER_META_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.meta.hh>

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

class motor_api(3D) ShaderProgramDescription : public Resource::Description
{
    MOTOR_NOCOPY(ShaderProgramDescription);

private:
    minitl::vector< ref< Shaders::Output > > m_outputs;

protected:
    ShaderProgramDescription(minitl::vector< ref< Shaders::Output > > outputs);
    ~ShaderProgramDescription();

public:
    virtual void buildSource(Shaders::IShaderBuilder & builder) const;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
