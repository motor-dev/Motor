/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <loaders/dx9shader.hh>
//#include    <loaders/dx9shaderbuilder.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace DirectX9 {

Dx9ShaderProgram::Dx9ShaderProgram(weak< const ShaderProgramDescription > shaderDescription,
                                   weak< const Dx9Renderer >              renderer)
    : IGPUResource(shaderDescription, renderer)
{
}

Dx9ShaderProgram::~Dx9ShaderProgram()
{
}

void Dx9ShaderProgram::load(weak< const Resource::Description > shaderDescription)
{
    motor_forceuse(shaderDescription);
}

void Dx9ShaderProgram::unload()
{
}

}}  // namespace Motor::DirectX9
