/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/core/threads/event.hh>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>
#include <win32/platformrenderer.hh>

namespace Motor { namespace Windowing {

static LRESULT CALLBACK WindowProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch(msg)
    {
    case WM_CLOSE:
    {
        // Window* win = (Window*)(GetWindowLongPtr(hWnd,GWLP_USERDATA));
        // motor_assert(win, "Motor window not associated with hWnd");
        // win->close();
        break;
    }

    case WM_PAINT:
    {
        ValidateRect(hWnd, nullptr);
        break;
    }

    case WM_SETFOCUS:
    case WM_KILLFOCUS: break;
    default: return DefWindowProc(hWnd, msg, wParam, lParam);
    }

    return 0;
}

Renderer::PlatformRenderer::PlatformRenderer(const weak< Renderer >& renderer)
    : m_renderer(renderer)
    , m_windowClassName(minitl::format< 128u >(FMT("__motor__{0}__"), (const void*)renderer))
    , m_wndClassEx {}
{
    // memset(&m_wndClassEx, 0, sizeof(WNDCLASSEX));
    m_wndClassEx.lpszClassName = m_windowClassName.c_str();
    m_wndClassEx.cbSize        = sizeof(WNDCLASSEX);
    m_wndClassEx.style         = CS_HREDRAW | CS_VREDRAW | CS_OWNDC;
    m_wndClassEx.lpfnWndProc   = WindowProc;
    m_wndClassEx.hInstance     = (HINSTANCE)::GetModuleHandle(nullptr);
    m_wndClassEx.hIcon         = nullptr;
    m_wndClassEx.hIconSm       = nullptr;
    m_wndClassEx.hCursor       = LoadCursor(nullptr, (LPCTSTR)IDC_ARROW);
    m_wndClassEx.hbrBackground = nullptr;
    m_wndClassEx.lpszMenuName  = nullptr;
    m_wndClassEx.cbClsExtra    = 0;
    m_wndClassEx.cbWndExtra    = sizeof(Window*);

    RegisterClassEx(&m_wndClassEx);
}

Renderer::PlatformRenderer::~PlatformRenderer()
{
    UnregisterClass(m_windowClassName.c_str(), (HINSTANCE)::GetModuleHandle(nullptr));
}

HWND Renderer::PlatformRenderer::createWindowImplementation(const WindowCreationFlags& flags) const
{
    HWND hWnd = CreateWindowEx(
        flags.fullscreen ? WS_EX_TOPMOST : 0, m_windowClassName.c_str(), flags.title, flags.flags,
        flags.x, flags.y, flags.size.right - flags.size.left, flags.size.bottom - flags.size.top,
        nullptr, nullptr, (HINSTANCE)::GetModuleHandle(nullptr), nullptr);
    return hWnd;
}

const istring& Renderer::PlatformRenderer::getWindowClassName() const
{
    return m_windowClassName;
}

void Renderer::PlatformRenderer::destroyWindowImplementation(HWND hWnd)
{
    motor_forceuse(this);
    DestroyWindow(hWnd);
}

//-----------------------------------------------------------------------------

Renderer::Renderer(minitl::Allocator& allocator, const weak< Resource::ResourceManager >& manager)
    : IRenderer(allocator, manager, Scheduler::MainThread)
    , m_platformRenderer(scoped< PlatformRenderer >::create(allocator, this))
{
}

Renderer::~Renderer() = default;

void Renderer::flush()
{
    IRenderer::flush();
    MSG msg;
    while(::PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE))
    {
        DispatchMessage(&msg);
    }
}

bool Renderer::hasPlatformRenderer() const
{
    return m_platformRenderer;
}

knl::uint2 Renderer::getScreenSize() const
{
    RECT rect;
    GetWindowRect(GetDesktopWindow(), &rect);
    return knl::uint2 {(u32)(rect.right - rect.left), (u32)(rect.bottom - rect.top)};
}

}}  // namespace Motor::Windowing
