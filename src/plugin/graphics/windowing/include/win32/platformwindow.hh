/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_WINDOWING_WIN32_PLATFORMWINDOW_HH
#define MOTOR_PLUGIN_GRAPHICS_WINDOWING_WIN32_PLATFORMWINDOW_HH

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <windows.h>

namespace Motor { namespace Windowing {
class Window;

class Window::PlatformWindow : public minitl::refcountable
{
    friend class Window;

private:
    weak< const Renderer > m_renderer;
    HWND                   m_window;

public:
    PlatformWindow(const weak< const Renderer >& renderer, const weak< Window >& window);
    ~PlatformWindow();
};

}}  // namespace Motor::Windowing

#endif
