/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <loaders/nullshader.hh>
#include <nullrenderer.hh>

namespace Motor { namespace Null {

NullShaderProgram::NullShaderProgram(
    const weak< const ShaderProgramDescription >& shaderDescription,
    const weak< const NullRenderer >&             renderer)
    : IGPUResource(shaderDescription, renderer)
{
}

NullShaderProgram::~NullShaderProgram() = default;

void NullShaderProgram::load(const weak< const Resource::IDescription >& /*shaderDescription*/)
{
}

void NullShaderProgram::unload()
{
}

}}  // namespace Motor::Null
