/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <loaders/nullwindow.hh>
#include <nullrenderer.hh>

namespace Motor { namespace Null {

void NullWindow::begin(ClearMode /*clear*/) const
{
}

void NullWindow::end(PresentMode /*presentMode*/) const
{
}

NullWindow::NullWindow(const weak< const RenderWindowDescription >& windowDescription,
                       const weak< const NullRenderer >&            renderer)
    : IRenderTarget(windowDescription, renderer)
{
}

NullWindow::~NullWindow() = default;

void NullWindow::present() const
{
}

void NullWindow::load(const weak< const Resource::IDescription >& /*windowDescription*/)
{
}

void NullWindow::unload()
{
}

}}  // namespace Motor::Null
