/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace OpenGLES {

class GLESWindow;

class GLESRenderer : public IRenderer
{
    friend class GLESWindow;

public:
    GLESRenderer(const Plugin::Context& context);
    ~GLESRenderer();

    u32 getMaxSimultaneousRenderTargets() const override
    {
        return 1;
    }
    void flush() override;

private:
    void attachWindow(weak< GLESWindow > w) const;

private:
    ref< IGPUResource >
    create(weak< const RenderSurfaceDescription > renderSurfaceDescription) const override;
    ref< IGPUResource >
    create(weak< const RenderWindowDescription > renderWindowDescription) const override;
    ref< IGPUResource >
               create(weak< const ShaderProgramDescription > shaderDescription) const override;
    knl::uint2 getScreenSize() const override;
};

}}  // namespace Motor::OpenGLES
