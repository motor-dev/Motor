/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WINDOWING_WINDOW_HH_
#define MOTOR_WINDOWING_WINDOW_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Windowing {

class Renderer;

class motor_api(WINDOWING) Window : public IRenderTarget
{
public:
    class PlatformWindow;

private:
    scoped< PlatformWindow > m_window;

protected:
    void* getWindowHandle() const;

public:
    Window(weak< const RenderWindowDescription > renderWindowDescription,
           weak< const Renderer >                renderer);
    ~Window();

    void load(weak< const Resource::IDescription > renderWindowDescription) override;
    void unload() override;

    uint2 getDimensions() const;
};

}}  // namespace Motor::Windowing

/**************************************************************************************************/
#endif
