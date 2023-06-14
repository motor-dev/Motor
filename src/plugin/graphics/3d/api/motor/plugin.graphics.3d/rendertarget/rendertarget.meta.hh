/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_RENDERTARGET_RENDERTARGET_META_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_RENDERTARGET_RENDERTARGET_META_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(3D) RenderTargetDescription
    : public Resource::Description< RenderTargetDescription >
{
protected:
    RenderTargetDescription();

public:
    ~RenderTargetDescription() override;
};

class motor_api(3D) RenderSurfaceDescription : public RenderTargetDescription
{
published:
    const knl::uint2 dimensions;
published:
    RenderSurfaceDescription(u16 width, u16 height);
    ~RenderSurfaceDescription() override;
};

class motor_api(3D) RenderWindowDescription : public RenderTargetDescription
{
published:
    const istring title;
published:
    explicit RenderWindowDescription(istring title);
    ~RenderWindowDescription() override;
};

}  // namespace Motor

#endif
