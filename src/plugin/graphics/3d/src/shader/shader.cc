/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/shader/ishaderbuilder.hh>
#include <motor/plugin.graphics.3d/shader/shader.script.hh>
#include <motor/plugin.graphics.3d/shader/types.script.hh>

namespace Motor {

ShaderProgramDescription::ShaderProgramDescription(minitl::vector< ref< Shaders::Output > > outputs)
    : m_outputs(outputs)
{
}

ShaderProgramDescription::~ShaderProgramDescription()
{
}

void ShaderProgramDescription::buildSource(Shaders::IShaderBuilder& /*builder*/) const
{
}

}  // namespace Motor
