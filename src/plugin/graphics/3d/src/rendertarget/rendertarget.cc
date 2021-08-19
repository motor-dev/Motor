/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.script.hh>

namespace Motor {

RenderTargetDescription::RenderTargetDescription()
{
}

RenderTargetDescription::~RenderTargetDescription()
{
}

RenderSurfaceDescription::RenderSurfaceDescription(u16 width, u16 height)
    : dimensions(make_uint2(width, height))
{
}

RenderSurfaceDescription::~RenderSurfaceDescription()
{
}

RenderWindowDescription::RenderWindowDescription(istring title) : title(title)
{
}

RenderWindowDescription::~RenderWindowDescription()
{
}

}  // namespace Motor
