/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_NULLRENDER_LOADERS_NULLWINDOW_HH
#define MOTOR_PLUGIN_GRAPHICS_NULLRENDER_LOADERS_NULLWINDOW_HH

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullWindow : public IRenderTarget
{
public:
    NullWindow(const weak< const RenderWindowDescription >& windowDescription,
               const weak< const NullRenderer >&            renderer);
    ~NullWindow() override;

private:
    void load(const weak< const Resource::IDescription >& windowDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::Null

#endif
