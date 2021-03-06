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

NullWindow::NullWindow(weak< const RenderWindowDescription > windowDescription,
                       weak< const NullRenderer >            renderer)
    : IRenderTarget(windowDescription, renderer)
{
}

NullWindow::~NullWindow()
{
}

void NullWindow::present() const
{
}

void NullWindow::load(weak< const Resource::IDescription > /*windowDescription*/)
{
}

void NullWindow::unload()
{
}

}}  // namespace Motor::Null
