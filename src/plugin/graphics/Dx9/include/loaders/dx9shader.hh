/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <d3d9.h>
#include <dx9renderer.hh>

namespace Motor { namespace DirectX9 {

class Dx9ShaderProgram : public IGPUResource
{
private:
    void load(weak< const Resource::IDescription > resource) override;
    void unload() override;

public:
    Dx9ShaderProgram(weak< const ShaderProgramDescription > shaderDescription,
                     weak< const Dx9Renderer >              renderer);
    ~Dx9ShaderProgram();
};

}}  // namespace Motor::DirectX9
