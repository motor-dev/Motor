/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <loaders/nullshader.hh>
#include <nullrenderer.hh>

namespace Motor { namespace Null {

NullShaderProgram::NullShaderProgram(weak< const ShaderProgramDescription > shaderDescription,
                                     weak< const NullRenderer >             renderer)
    : IGPUResource(shaderDescription, renderer)
{
}

NullShaderProgram::~NullShaderProgram()
{
}

void NullShaderProgram::load(weak< const Resource::IDescription > /*shaderDescription*/)
{
}

void NullShaderProgram::unload()
{
}

}}  // namespace Motor::Null
