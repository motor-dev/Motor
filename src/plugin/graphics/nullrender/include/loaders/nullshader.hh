/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_NULLRENDER_LOADERS_NULLSHADER_HH_
#define MOTOR_NULLRENDER_LOADERS_NULLSHADER_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullShaderProgram : public IGPUResource
{
public:
    NullShaderProgram(weak< const ShaderProgramDescription > shaderDescription,
                      weak< const NullRenderer >             renderer);
    ~NullShaderProgram();

private:
    void load(weak< const Resource::IDescription > shaderDescription) override;
    void unload() override;
};

}}  // namespace Motor::Null

/**************************************************************************************************/
#endif
