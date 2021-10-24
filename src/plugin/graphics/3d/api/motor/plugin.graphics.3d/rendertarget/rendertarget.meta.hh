/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_RENDERTARGET_RENDERTARGET_SCRIPT_HH_
#define MOTOR_3D_RENDERTARGET_RENDERTARGET_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.meta.hh>

namespace Motor {

class motor_api(3D) RenderTargetDescription : public Resource::Description
{
    MOTOR_NOCOPY(RenderTargetDescription);

protected:
    RenderTargetDescription();

public:
    ~RenderTargetDescription();
};

class motor_api(3D) RenderSurfaceDescription : public RenderTargetDescription
{
    MOTOR_NOCOPY(RenderSurfaceDescription);
published:
    const uint2 dimensions;
published:
    RenderSurfaceDescription(u16 width, u16 height);
    ~RenderSurfaceDescription();
};

class motor_api(3D) RenderWindowDescription : public RenderTargetDescription
{
    MOTOR_NOCOPY(RenderWindowDescription);
published:
    const istring title;
published:
    RenderWindowDescription(istring title);
    ~RenderWindowDescription();
};

}  // namespace Motor

/**************************************************************************************************/
#endif