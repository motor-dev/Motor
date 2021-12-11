/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_DX9_LOADERS_DX9WINDOW_HH_
#define MOTOR_DX9_LOADERS_DX9WINDOW_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/plugin.graphics.windowing/window.hh>
#include <d3d9.h>
#include <dx9renderer.hh>

namespace Motor { namespace DirectX9 {

class Dx9Window : public Windowing::Window
{
    MOTOR_NOCOPY(Dx9Window);

private:
    LPDIRECT3DSWAPCHAIN9 m_swapChain;

private:
    void setCurrent() const;

    void load(weak< const Resource::IDescription > windowDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

public:
    Dx9Window(weak< const RenderWindowDescription > resource, weak< const Dx9Renderer > renderer);
    ~Dx9Window();
};

}}  // namespace Motor::DirectX9

/**************************************************************************************************/
#endif
