/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>

namespace Motor {

RenderTargetDescription::RenderTargetDescription() = default;

RenderTargetDescription::~RenderTargetDescription() = default;

RenderSurfaceDescription::RenderSurfaceDescription(u16 width, u16 height)
    : dimensions(knl::uint2 {width, height})
{
    motor_forceuse(this->dimensions);
}

RenderSurfaceDescription::~RenderSurfaceDescription() = default;

RenderWindowDescription::RenderWindowDescription(istring title) : title(title)
{
    motor_forceuse(this->title);
}

RenderWindowDescription::~RenderWindowDescription() = default;

}  // namespace Motor
