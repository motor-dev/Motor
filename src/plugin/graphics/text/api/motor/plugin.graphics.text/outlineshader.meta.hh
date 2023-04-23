/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>

namespace Motor {

class motor_api(TEXT) OutlineShader : public ShaderProgramDescription
{
    friend class OutlineShaderManager;
published:
    OutlineShader(const weak< Shaders::Float4 >& textColor,
                  const weak< Shaders::Float4 >& backgroundColor);
    ~OutlineShader() override;
};

}  // namespace Motor
