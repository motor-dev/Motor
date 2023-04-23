/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>
#include <X11/X.h>
#include <X11/Xatom.h>
#include <X11/Xlib.h>
#include <posix/platformrenderer.hh>

namespace Motor { namespace Windowing {

class Window::PlatformWindow : public minitl::refcountable
{
    friend class Window;

private:
    ::Display* m_display;
    ::Window   m_window;

public:
    PlatformWindow(::Display* display, ::Window window);
    ~PlatformWindow() override;
};

Window::PlatformWindow::PlatformWindow(::Display* display, ::Window window)
    : m_display(display)
    , m_window(window)
{
}

Window::PlatformWindow::~PlatformWindow()
{
    XDestroyWindow(m_display, m_window);
}

Window::Window(const weak< const RenderWindowDescription >& renderWindowDescription,
               const weak< const Renderer >&                renderer)
    : IRenderTarget(renderWindowDescription, renderer)
    , m_window()
{
}

Window::~Window() = default;

void Window::load(const weak< const Resource::IDescription >& /*renderWindowDescription*/)
{
    m_window.reset(
        scoped< PlatformWindow >::create(m_renderer->arena(),
                                         motor_checked_cast< const Renderer >(m_renderer)
                                             ->m_platformRenderer->m_platformData.display,
                                         motor_checked_cast< const Renderer >(m_renderer)
                                             ->m_platformRenderer->createWindow(0, 0, 200, 200)));
    Window* w = this;
    XChangeProperty(
        motor_checked_cast< const Renderer >(m_renderer)
            ->m_platformRenderer->m_platformData.display,
        m_window->m_window,
        motor_checked_cast< const Renderer >(m_renderer)->m_platformRenderer->m_windowProperty,
        XA_INTEGER, 8, PropModeReplace, (unsigned char*)&w,
        (int)sizeof(w));  // NOLINT(bugprone-sizeof-expression)
}

void Window::unload()
{
    m_window.reset(scoped< PlatformWindow >());
}

void* Window::getWindowHandle() const
{
    if(motor_assert(m_window, "no window implementation is created")) return nullptr;
    return (void*)&m_window->m_window;
}

knl::uint2 Window::getDimensions() const
{
    motor_forceuse(this);
    return knl::uint2 {1920, 1200};
}

}}  // namespace Motor::Windowing
