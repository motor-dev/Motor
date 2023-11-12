/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>
#include <darwin/platformrenderer.hh>

#ifndef MAC_OS_X_VERSION_10_12
#    define MAC_OS_X_VERSION_10_12 101200
#endif

#if __MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_12
#    define NSWindowStyleMaskTitled    NSTitledWindowMask
#    define NSWindowStyleMaskResizable NSResizableWindowMask
#endif

namespace Motor { namespace Windowing {

class Window::PlatformWindow : public minitl::pointer
{
    friend class Window;

private:
    NSWindow* m_window;

public:
    PlatformWindow(u32 w, u32 h);
    ~PlatformWindow() override = default;
};

Window::PlatformWindow::PlatformWindow(u32 w, u32 h)
    : m_window([[NSWindow alloc]
        initWithContentRect:NSMakeRect(0, 0, w, h)
                  styleMask:NSWindowStyleMaskTitled | NSWindowStyleMaskResizable
                    backing:NSBackingStoreBuffered
                      defer:NO])
{
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
    knl::uint2 dimensions
        = knl::uint2 {800, 600};  // motor_checked_cast<const RenderWindow>(resource)->dimensions;
    m_window = scoped< PlatformWindow >::create(m_renderer->arena(), dimensions._0, dimensions._1);
}

void Window::unload()
{
    m_window = scoped< PlatformWindow >();
}

void* Window::getWindowHandle() const
{
    if(motor_assert(m_window, "no window implementation is created")) return nullptr;
    return (void*)m_window->m_window;
}

knl::uint2 Window::getDimensions() const
{
    return knl::uint2 {1920, 1200};
}

}}  // namespace Motor::Windowing
