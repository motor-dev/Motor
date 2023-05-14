/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.GL4/glmemoryhost.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <extensions.hh>

#include <motor/core/threads/thread.hh>
#include <motor/plugin.graphics.3d/mesh/mesh.meta.hh>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <loaders/rendertarget/glwindow.hh>

#include <GL/glx.h>
#include <GL/glxext.h>

namespace Motor { namespace OpenGL {

#define GLX_CONTEXT_MAJOR_VERSION_ARB 0x2091
#define GLX_CONTEXT_MINOR_VERSION_ARB 0x2092
typedef GLXContext (*glXCreateContextAttribsARBProc)(Display*, GLXFBConfig, GLXContext, Bool,
                                                     const int*);

struct PlatformData
{
    ::Display*     display;
    ::GLXFBConfig  fbConfig;
    ::XVisualInfo* visual;
};

class GLRenderer::Context : public minitl::refcountable
{
    friend class GLRenderer;
    friend class GLWindow;

private:
    typedef int (*FGLXSwapInterval)(int);

private:
    ::Display*       m_display;
    ::Window         m_defaultWindow;
    GLXContext       m_glContext;
    u64              m_threadId;
    FGLXSwapInterval glXSwapInterval;

public:
    const ShaderExtensions shaderext;

public:
    explicit Context(PlatformData* data);
    ~Context() override;
};

static GLXContext createGLXContext(::Display* display, ::GLXFBConfig fbConfig)
{
    GLXContext context = nullptr;
    GLXContext ctx_old
        = glXCreateContext(display, glXGetVisualFromFBConfig(display, fbConfig), nullptr, GL_TRUE);
    motor_assert(ctx_old, "could not create legacy OpenGL context");
    auto glXCreateContextAttribsARB = (glXCreateContextAttribsARBProc)glXGetProcAddress(
        (const GLubyte*)"glXCreateContextAttribsARB");
    if(glXCreateContextAttribsARB)
    {
        int attribs[][10]
            = {{GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 6,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 5,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 4,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 3,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 2,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 1,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 4, GLX_CONTEXT_MINOR_VERSION_ARB, 0,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 3, GLX_CONTEXT_MINOR_VERSION_ARB, 3,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 3, GLX_CONTEXT_MINOR_VERSION_ARB, 2,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 3, GLX_CONTEXT_MINOR_VERSION_ARB, 1,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 3, GLX_CONTEXT_MINOR_VERSION_ARB, 0,
                GLX_CONTEXT_FLAGS_ARB, GLX_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB, None},
               {GLX_CONTEXT_MAJOR_VERSION_ARB, 2, GLX_CONTEXT_MINOR_VERSION_ARB, 1, None}};
        XSync(display, False);
        for(auto& attrib: attribs)
        {
            context = glXCreateContextAttribsARB(display, fbConfig, nullptr, True, attrib);
            if(context) break;
        }
    }
    if(!context)
    {
        context = glXCreateNewContext(display, fbConfig, GLX_RGBA_TYPE, nullptr, True);
    }
    glXMakeCurrent(display, 0, nullptr);
    glXDestroyContext(display, ctx_old);
    return context;
}

static ::Window createDefaultWindow(::Display* display, ::XVisualInfo* visual)
{
    XSetWindowAttributes attributes;
    attributes.colormap
        = XCreateColormap(display, XRootWindow(display, visual->screen), visual->visual, AllocNone);
    attributes.border_pixel      = 0;
    attributes.override_redirect = false;  // flags.fullscreen
    attributes.event_mask  = ExposureMask | KeyPressMask | ButtonPressMask | StructureNotifyMask;
    int      attributeMask = CWBorderPixel | CWEventMask | CWOverrideRedirect | CWColormap;
    ::Window result
        = XCreateWindow(display, XRootWindow(display, visual->screen), 1, 1, 1, 1, 1, visual->depth,
                        InputOutput, visual->visual, attributeMask, &attributes);
    XSync(display, false);
    return result;
}

GLRenderer::Context::Context(PlatformData* data)
    : m_display(data->display)
    , m_defaultWindow(createDefaultWindow(m_display, data->visual))
    , m_glContext(createGLXContext(data->display, data->fbConfig))
    , m_threadId(Thread::currentId())
    , shaderext()
{
    glXMakeCurrent(m_display, m_defaultWindow, m_glContext);
    motor_info_format(Log::gl(), "Creating OpenGL {0} ({1}) on {2}",
                      (const char*)glGetString(GL_VERSION), (const char*)glGetString(GL_VENDOR),
                      (const char*)glGetString(GL_RENDERER));
    glXSwapInterval = (FGLXSwapInterval)glXGetProcAddress((const GLubyte*)"glXSwapIntervalMESA");
    if(!glXSwapInterval)
        glXSwapInterval = (FGLXSwapInterval)glXGetProcAddress((const GLubyte*)"glXSwapIntervalEXT");
    if(!glXSwapInterval)
        glXSwapInterval = (FGLXSwapInterval)glXGetProcAddress((const GLubyte*)"glXSwapIntervalSGI");
}

GLRenderer::Context::~Context()
{
    XDestroyWindow(m_display, m_defaultWindow);
}

class GLWindow::Context : public minitl::refcountable
{
    friend class GLRenderer;
    friend class GLWindow;

private:
    ::Display* m_display;
    GLXContext m_glContext;
#if MOTOR_ENABLE_ASSERT
    u64 m_threadId;
#endif

public:
    Context(::Display* display, GLXContext context, u64 threadId);
    ~Context() override;
};

GLWindow::Context::Context(::Display* display, GLXContext context, u64 threadId)
    : m_display(display)
    , m_glContext(context)
#if MOTOR_ENABLE_ASSERT
    , m_threadId(threadId)
#endif
{
    motor_forceuse(threadId);
}

GLWindow::Context::~Context() = default;

//------------------------------------------------------------------------

GLRenderer::GLRenderer(const Plugin::Context& context)
    : Windowing::Renderer(Arena::general(), context.resourceManager)
    , m_context(hasPlatformRenderer() ? scoped< Context >::create(
                    Arena::general(), static_cast< PlatformData* >(getPlatformData()))
                                      : scoped< Context >())
    , m_openGLMemoryHost(scoped< GLMemoryHost >::create(Arena::general()))
    , m_openCLScheduler(inamespace("plugin.compute.opencl_gl"), context)
{
}

GLRenderer::~GLRenderer()
{
    GLRenderer::flush();
}

void GLRenderer::attachWindow(const weak< GLWindow >& w) const
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    w->m_context.reset(scoped< GLWindow::Context >::create(
        Arena::general(), m_context->m_display, m_context->m_glContext, m_context->m_threadId));
    if(m_context->glXSwapInterval)
    {
        w->setCurrent();
        (*m_context->glXSwapInterval)(0);
        w->clearCurrent();
    }
}

const ShaderExtensions& GLRenderer::shaderext() const
{
    motor_assert(m_context, "extensions required before context was created");
    return m_context->shaderext;
}

bool GLRenderer::success() const
{
    return hasPlatformRenderer() && m_context != nullptr;
}

//------------------------------------------------------------------------

GLWindow::GLWindow(const weak< const RenderWindowDescription >& renderwindow,
                   const weak< const GLRenderer >&              renderer)
    : Windowing::Window(renderwindow, renderer)
    , m_context(scoped< Context >())
{
    motor_info_format(Log::gl(), "creating window {0}", renderwindow->title);
}

void GLWindow::load(const weak< const Resource::IDescription >& description)
{
    Window::load(description);
    motor_checked_cast< const GLRenderer >(m_renderer)->attachWindow(this);
}

void GLWindow::unload()
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    Window::unload();
    m_context.reset(scoped< Context >());
}

void GLWindow::setCurrent() const
{
    if(m_context)
    {
        motor_assert(Thread::currentId() == m_context->m_threadId,
                     "render command on wrong thread");
        auto* w = (::Window*)getWindowHandle();
        if(!glXMakeCurrent(m_context->m_display, *w, m_context->m_glContext))
            motor_error(Log::gl(), "Unable to set current context");
    }
}

void GLWindow::clearCurrent() const
{
    if(m_context)
    {
        motor_assert(Thread::currentId() == m_context->m_threadId,
                     "render command on wrong thread");
        weak< GLRenderer::Context > c
            = motor_checked_cast< const GLRenderer >(m_renderer)->m_context;
        if(!glXMakeCurrent(c->m_display, c->m_defaultWindow, c->m_glContext))
            motor_error(Log::gl(), "Unable to clear current context");
    }
}

void GLWindow::present() const
{
    if(m_context)
    {
        motor_assert(Thread::currentId() == m_context->m_threadId,
                     "render command on wrong thread");
        auto* w = (::Window*)getWindowHandle();
        glXSwapBuffers(motor_checked_cast< const GLRenderer >(m_renderer)->m_context->m_display,
                       *w);
    }
}

}}  // namespace Motor::OpenGL
