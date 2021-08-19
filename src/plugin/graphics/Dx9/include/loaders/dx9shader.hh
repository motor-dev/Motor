/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_DX9_LOADERS_DX9SHADER_HH_
#define MOTOR_DX9_LOADERS_DX9SHADER_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <d3d9.h>
#include <dx9renderer.hh>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace DirectX9 {

class Dx9ShaderProgram : public IGPUResource
{
private:
    void load(weak< const Resource::Description > resource) override;
    void unload() override;

public:
    Dx9ShaderProgram(weak< const ShaderProgramDescription > shaderDescription,
                     weak< const Dx9Renderer >              renderer);
    ~Dx9ShaderProgram();
};

}}  // namespace Motor::DirectX9

/**************************************************************************************************/
#endif
