/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullSurface : public IRenderTarget
{
public:
    NullSurface(const weak< const RenderSurfaceDescription >& resource,
                const weak< const NullRenderer >&             renderer);
    ~NullSurface() override;

private:
    void load(const weak< const Resource::IDescription >& surfaceDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::Null
