/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/scheduler/scheduler.hh>
#include <glesrenderer.hh>

namespace Motor { namespace OpenGLES {

GLESRenderer::GLESRenderer(const Plugin::Context& context)
    : IRenderer(Arena::general(), context.resourceManager, Scheduler::MainThread)
{
}

GLESRenderer::~GLESRenderer()
{
    flush();
}

void GLESRenderer::flush()
{
    IRenderer::flush();
}

ref< IGPUResource >
GLESRenderer::create(weak< const RenderSurfaceDescription > /*renderSurfaceDescription*/) const
{
    return ref< IGPUResource >();
}

ref< IGPUResource >
GLESRenderer::create(weak< const RenderWindowDescription > /*renderWindowDescription*/) const
{
    return ref< IGPUResource >();
}

ref< IGPUResource >
GLESRenderer::create(weak< const ShaderProgramDescription > /*shaderDescription*/) const
{
    return ref< IGPUResource >();
}

knl::uint2 GLESRenderer::getScreenSize() const
{
    return knl::make_uint2(320, 200);
}

}}  // namespace Motor::OpenGLES
