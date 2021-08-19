/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_NULLRENDER_LOADERS_NULLSURFACE_HH_
#define MOTOR_NULLRENDER_LOADERS_NULLSURFACE_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullSurface : public IRenderTarget
{
public:
    NullSurface(weak< const RenderSurfaceDescription > resource,
                weak< const NullRenderer >             renderer);
    ~NullSurface();

private:
    void load(weak< const Resource::Description > surfaceDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::Null

/**************************************************************************************************/
#endif
