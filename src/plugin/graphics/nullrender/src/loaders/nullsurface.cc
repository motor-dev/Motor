/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <loaders/nullsurface.hh>
#include <nullrenderer.hh>

namespace Motor { namespace Null {

void NullSurface::begin(ClearMode /*clear*/) const
{
}

void NullSurface::end(PresentMode /*presentMode*/) const
{
}

NullSurface::NullSurface(weak< const RenderSurfaceDescription > surfaceDescription,
                         weak< const NullRenderer >             renderer)
    : IRenderTarget(surfaceDescription, renderer)
{
}

NullSurface::~NullSurface()
{
}

void NullSurface::present() const
{
}

void NullSurface::load(weak< const Resource::IDescription > /*surfaceDescription*/)
{
}

void NullSurface::unload()
{
}

}}  // namespace Motor::Null
