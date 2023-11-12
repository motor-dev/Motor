/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <nullrenderer.hh>

#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <loaders/nullshader.hh>
#include <loaders/nullsurface.hh>
#include <loaders/nullwindow.hh>

namespace Motor { namespace Null {

void NullRenderer::flush()
{
    IRenderer::flush();
}

NullRenderer::NullRenderer(const Plugin::Context& context)
    : IRenderer(Arena::general(), context.resourceManager)
{
}

NullRenderer::~NullRenderer()
{
    NullRenderer::flush();
}

scoped< IGPUResource >
NullRenderer::create(weak< const RenderSurfaceDescription > renderSurfaceDescription) const
{
    return scoped< NullSurface >::create(m_allocator, renderSurfaceDescription, this);
}

scoped< IGPUResource >
NullRenderer::create(weak< const RenderWindowDescription > renderWindowDescription) const
{
    return scoped< NullWindow >::create(m_allocator, renderWindowDescription, this);
}

scoped< IGPUResource >
NullRenderer::create(weak< const ShaderProgramDescription > shaderDescription) const
{
    return scoped< NullShaderProgram >::create(m_allocator, shaderDescription, this);
}

}}  // namespace Motor::Null
