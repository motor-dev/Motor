/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_NULLRENDER_RENDERER_HH_
#define MOTOR_NULLRENDER_RENDERER_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Null {

class NullRenderer : public IRenderer
{
    MOTOR_NOCOPY(NullRenderer);

public:
    NullRenderer(const Plugin::Context& context);
    ~NullRenderer();

    u32 getMaxSimultaneousRenderTargets() const override
    {
        return 1;
    }

    void  flush() override;
    uint2 getScreenSize() const override
    {
        return make_uint2(1920, 1080);
    }

private:
    ref< IGPUResource >
    create(weak< const RenderSurfaceDescription > renderSurfaceDescription) const override;
    ref< IGPUResource >
    create(weak< const RenderWindowDescription > renderWindowDescription) const override;
    ref< IGPUResource >
    create(weak< const ShaderProgramDescription > shaderDescription) const override;
};

}}  // namespace Motor::Null

/**************************************************************************************************/
#endif
