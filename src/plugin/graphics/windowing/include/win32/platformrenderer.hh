/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_WINDOWING_WIN32_PLATFORMRENDERER_HH
#define MOTOR_PLUGIN_GRAPHICS_WINDOWING_WIN32_PLATFORMRENDERER_HH

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/core/threads/thread.hh>
#include <windows.h>

namespace Motor { namespace Windowing {

struct WindowCreationFlags
{
    const char* title;
    int         x;
    int         y;
    RECT        size;
    DWORD       flags;
    bool        fullscreen;
};

class Renderer::PlatformRenderer : public minitl::pointer
{
private:
    weak< Renderer > m_renderer;
    istring          m_windowClassName;
    WNDCLASSEX       m_wndClassEx;

public:
    PlatformRenderer(const weak< Renderer >& renderer);
    ~PlatformRenderer() override;

    HWND           createWindowImplementation(const WindowCreationFlags& flags) const;
    void           destroyWindowImplementation(HWND hWnd);
    const istring& getWindowClassName() const;
};

}}  // namespace Motor::Windowing

#endif
