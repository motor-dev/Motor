/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_WINDOWING_RENDERER_HH
#define MOTOR_PLUGIN_GRAPHICS_WINDOWING_RENDERER_HH

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>

namespace Motor { namespace Windowing {

class Window;
struct WindowCreationFlags;

class motor_api(WINDOWING) Renderer : public IRenderer
{
    friend class Window;
    friend class Window::PlatformWindow;

private:
    class PlatformRenderer;
    friend class PlatformRenderer;
    scoped< PlatformRenderer > m_platformRenderer;

protected:
    void flush() override;
    bool hasPlatformRenderer() const;

public:
    Renderer(minitl::allocator & arena, const weak< Resource::ResourceManager >& manager);
    ~Renderer() override;

    knl::uint2 getScreenSize() const override;
    void*      getPlatformData();
};

}}  // namespace Motor::Windowing

#endif
