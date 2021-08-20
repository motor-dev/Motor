/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <loaders/rendertarget/glsurface.hh>
#include <loaders/rendertarget/glwindow.hh>
#include <loaders/shader/glshader.hh>

namespace Motor { namespace OpenGL {

void GLRenderer::flush()
{
    Windowing::Renderer::flush();
}

ref< IGPUResource >
    GLRenderer::create(weak< const RenderSurfaceDescription > /*renderSurfaceDescription*/) const
{
    return ref< GLSurface >();
}

ref< IGPUResource >
GLRenderer::create(weak< const RenderWindowDescription > renderWindowDescription) const
{
    return ref< GLWindow >::create(m_allocator, renderWindowDescription, this);
}

ref< IGPUResource >
GLRenderer::create(weak< const ShaderProgramDescription > shaderDescription) const
{
    return ref< GLShaderProgram >::create(m_allocator, shaderDescription, this);
}

}}  // namespace Motor::OpenGL
