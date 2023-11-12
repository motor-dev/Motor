/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_GLES2_GLESRENDERER_HH
#define MOTOR_PLUGIN_GRAPHICS_GLES2_GLESRENDERER_HH

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace OpenGLES {

class GLESWindow;

class GLESRenderer : public IRenderer
{
    friend class GLESWindow;

public:
    explicit GLESRenderer(const Plugin::Context& context);
    ~GLESRenderer() override;

    u32 getMaxSimultaneousRenderTargets() const override
    {
        return 1;
    }
    void flush() override;

private:
    scoped< IGPUResource >
    create(weak< const RenderSurfaceDescription > renderSurfaceDescription) const override;
    scoped< IGPUResource >
    create(weak< const RenderWindowDescription > renderWindowDescription) const override;
    scoped< IGPUResource >
               create(weak< const ShaderProgramDescription > shaderDescription) const override;
    knl::uint2 getScreenSize() const override;
};

}}  // namespace Motor::OpenGLES

#endif
