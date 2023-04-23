/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>
#include <motor/plugin.graphics.text/outlineshader.meta.hh>

namespace Motor {

minitl::vector< ref< Shaders::Output > >
createOutlineShader(const weak< Shaders::Float4 >& textColor,
                    const weak< Shaders::Float4 >& backgroundColor)
{
    motor_forceuse(textColor);
    motor_forceuse(backgroundColor);
    minitl::vector< ref< Shaders::Output > > result(Arena::temporary());
    result.reserve(1);
    // result.push_back();
    return result;
}

OutlineShader::OutlineShader(const weak< Shaders::Float4 >& textColor,
                             const weak< Shaders::Float4 >& backgroundColor)
    : ShaderProgramDescription(createOutlineShader(textColor, backgroundColor))
{
}

OutlineShader::~OutlineShader() = default;

}  // namespace Motor
