/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Windowing {

class Renderer;

class motor_api(WINDOWING) Window : public IRenderTarget
{
public:
    class PlatformWindow;

private:
    scoped< PlatformWindow > m_window;

protected:
    void* getWindowHandle() const;

public:
    Window(const weak< const RenderWindowDescription >& renderWindowDescription,
           const weak< const Renderer >&                renderer);
    ~Window() override;

    void load(const weak< const Resource::IDescription >& renderWindowDescription) override;
    void unload() override;

    knl::uint2 getDimensions() const;
};

}}  // namespace Motor::Windowing
