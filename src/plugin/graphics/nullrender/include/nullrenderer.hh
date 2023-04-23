/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Null {

class NullRenderer : public IRenderer
{
public:
    explicit NullRenderer(const Plugin::Context& context);
    ~NullRenderer() override;

    u32 getMaxSimultaneousRenderTargets() const override
    {
        return 1;
    }

    void       flush() override;
    knl::uint2 getScreenSize() const override
    {
        return knl::uint2 {1920, 1080};
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
