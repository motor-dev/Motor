/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <extensions.hh>
#include <loaders/rendertarget/glsurface.hh>

namespace Motor { namespace OpenGL {

GLSurface::GLSurface(weak< const RenderSurfaceDescription > surfaceDescription,
                     weak< GLRenderer >                     renderer)
    : IRenderTarget(surfaceDescription, renderer)
{
}

GLSurface::~GLSurface()
{
}

void GLSurface::load(weak< const Resource::IDescription > /*surfaceDescription*/)
{
}

void GLSurface::unload()
{
}

void GLSurface::begin(ClearMode clear) const
{
    setCurrent();
    if(clear == IRenderTarget::Clear)
    {
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
    }
}

void GLSurface::end(PresentMode presentMode) const
{
    glFlush();
    if(presentMode == Present)
    {
        present();
    }
    clearCurrent();
}

void GLSurface::setCurrent() const
{
}

void GLSurface::clearCurrent() const
{
}

void GLSurface::present() const
{
}

}}  // namespace Motor::OpenGL
