/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>
#include <win32/platformrenderer.hh>
#include <win32/platformwindow.hh>

namespace Motor { namespace Windowing {

#ifdef _MSC_VER
#    pragma warning(push)
#    pragma warning(disable : 4505)
#endif
static inline void displayError()
{
    char* msg;
    ::FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, nullptr,
                     ::GetLastError(), 0, (char*)&msg, 0, nullptr);
    MessageBoxA(nullptr, msg, "Win32 error", MB_OK);
    ::LocalFree(msg);
}

#ifdef _MSC_VER
#    pragma warning(pop)
#endif

Window::PlatformWindow::PlatformWindow(const weak< const Renderer >& renderer,
                                       const weak< Window >&         window)
    : m_renderer(renderer)
    , m_window {}
{
    WindowCreationFlags f {};
    f.title = "TODO";
    f.flags = /*TODO*/ WS_CAPTION | WS_THICKFRAME | WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX;
    f.x     = 0;
    f.y     = 0;
    f.size.left   = 0;
    f.size.right  = 800;
    f.size.top    = 0;
    f.size.bottom = 600;
    f.fullscreen  = false;
    AdjustWindowRect(
        &f.size, WS_CAPTION | WS_THICKFRAME | WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX, FALSE);
    m_window = renderer->m_platformRenderer->createWindowImplementation(f);
    if(!m_window)
    {
        displayError();
    }
    SetWindowLongPtr(m_window, GWLP_USERDATA, (LONG_PTR)window.operator->());
    ShowWindow(m_window, SW_SHOW);
    UpdateWindow(m_window);
}

Window::PlatformWindow::~PlatformWindow()
{
    HWND hWnd = m_window;
    m_window  = nullptr;
    if(hWnd) m_renderer->m_platformRenderer->destroyWindowImplementation(hWnd);
}

Window::Window(const weak< const RenderWindowDescription >& renderWindowDescription,
               const weak< const Renderer >&                renderer)
    : IRenderTarget(renderWindowDescription, renderer)
    , m_window(scoped< PlatformWindow >())
{
}

Window::~Window() = default;

void Window::load(const weak< const Resource::IDescription >& renderWindowDescription)
{
    motor_forceuse(renderWindowDescription);
    m_window = scoped< PlatformWindow >::create(
        m_renderer->arena(), motor_checked_cast< const Renderer >(m_renderer), this);
}

void Window::unload()
{
    m_window = scoped< PlatformWindow >();
}

knl::uint2 Window::getDimensions() const
{
    RECT r;
    GetClientRect(m_window->m_window, &r);
    return knl::uint2 {(u32)(r.right - r.left), (u32)(r.bottom - r.top)};
}

void* Window::getWindowHandle() const
{
    if(motor_assert(m_window, "no window implementation is created")) return nullptr;
    return (void*)&m_window->m_window;
}

}}  // namespace Motor::Windowing
