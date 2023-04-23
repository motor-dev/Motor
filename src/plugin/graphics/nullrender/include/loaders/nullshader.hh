/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullShaderProgram : public IGPUResource
{
public:
    NullShaderProgram(const weak< const ShaderProgramDescription >& shaderDescription,
                      const weak< const NullRenderer >&             renderer);
    ~NullShaderProgram() override;

private:
    void load(const weak< const Resource::IDescription >& shaderDescription) override;
    void unload() override;
};

}}  // namespace Motor::Null
