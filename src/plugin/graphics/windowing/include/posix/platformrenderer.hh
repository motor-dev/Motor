/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WINDOWING_POSIX_RENDERER_HH_
#define MOTOR_WINDOWING_POSIX_RENDERER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.windowing/stdafx.h>
#include <GL/glx.h>
#include <X11/Xatom.h>
#include <motor/plugin.graphics.windowing/renderer.hh>

namespace Motor { namespace Windowing {

struct PlatformData
{
    ::Display*     display;
    ::GLXFBConfig  fbConfig;
    ::XVisualInfo* visual;
    ::Atom         wm_protocols;
    ::Atom         wm_delete_window;
    PlatformData(::Display* display);
};

class Renderer::PlatformRenderer : public minitl::refcountable
{
    friend class Renderer;
    friend class Window;

private:
    PlatformData m_platformData;
    ::Atom       m_windowProperty;

private:
    static int xError(::Display* display, XErrorEvent* event);
    static int ioError(::Display* display);

public:
    PlatformRenderer();
    ~PlatformRenderer();
    ::Window createWindow(i16 x, i16 y, u16 w, u16 h);

    weak< Window > getWindowFromXWindow(::Window w);
};

}}  // namespace Motor::Windowing

/**************************************************************************************************/
#endif
