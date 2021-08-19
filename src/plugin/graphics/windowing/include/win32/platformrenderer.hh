/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WINDOWING_WIN32_PLATFORMRENDERER_HH_
#define MOTOR_WINDOWING_WIN32_PLATFORMRENDERER_HH_
/**************************************************************************************************/
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

class Renderer::PlatformRenderer : public minitl::refcountable
{
    MOTOR_NOCOPY(PlatformRenderer);

private:
    weak< Renderer > m_renderer;
    istring          m_windowClassName;
    WNDCLASSEX       m_wndClassEx;

public:
    PlatformRenderer(weak< Renderer > renderer);
    ~PlatformRenderer();

    HWND           createWindowImplementation(const WindowCreationFlags& flags) const;
    void           destroyWindowImplementation(HWND hWnd);
    const istring& getWindowClassName() const;
};

}}  // namespace Motor::Windowing

/**************************************************************************************************/
#endif
