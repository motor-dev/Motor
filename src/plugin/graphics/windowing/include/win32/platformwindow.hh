/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <windows.h>

namespace Motor { namespace Windowing {
class Window;

class Window::PlatformWindow : public minitl::refcountable
{
    friend class Window;
    MOTOR_NOCOPY(PlatformWindow);

private:
    weak< const Renderer > m_renderer;
    HWND                   m_window;

public:
    PlatformWindow(weak< const Renderer > renderer, weak< Window > window);
    ~PlatformWindow();
};

}}  // namespace Motor::Windowing
