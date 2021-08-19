/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WINDOWING_RENDERER_HH_
#define MOTOR_WINDOWING_RENDERER_HH_
/**************************************************************************************************/
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
    MOTOR_NOCOPY(Renderer);

private:
    class PlatformRenderer;
    friend class PlatformRenderer;
    scoped< PlatformRenderer > m_platformRenderer;

protected:
    void flush() override;

protected:
    void* createDummyHandle();

public:
    Renderer(minitl::Allocator & allocator, weak< Resource::ResourceManager > manager);
    ~Renderer();

    uint2 getScreenSize() const override;
    void* getPlatformData();
    bool  success() const;
};

}}  // namespace Motor::Windowing

/**************************************************************************************************/
#endif
