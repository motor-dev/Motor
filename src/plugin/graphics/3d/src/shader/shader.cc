/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/shader/ishaderbuilder.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>

namespace Motor {

ShaderProgramDescription::ShaderProgramDescription(minitl::vector< ref< Shaders::Output > > outputs)
    : m_outputs(minitl::move(outputs))
{
}

ShaderProgramDescription::~ShaderProgramDescription() = default;

void ShaderProgramDescription::buildSource(Shaders::IShaderBuilder& /*builder*/) const
{
}

}  // namespace Motor
