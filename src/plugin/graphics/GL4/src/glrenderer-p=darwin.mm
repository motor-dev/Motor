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
#include <motor/plugin.graphics.3d/texture/texture.meta.hh>
#include <loaders/mesh/glmesh.hh>
#include <loaders/rendertarget/glwindow.hh>
#include <loaders/shader/glshader.hh>
#include <loaders/texture/gltexture.hh>

#include <Cocoa/Cocoa.h>
#include <OpenGL/OpenGL.h>

@interface MotorOpenGLView : NSView
{
@public
    NSOpenGLContext* m_context;
}

- (id)initWithFrame:(NSRect)frame context:(NSOpenGLContext*)context;

@end

@implementation MotorOpenGLView

- (id)initWithFrame:(NSRect)frame context:(NSOpenGLContext*)context
{
    [super initWithFrame:frame];
    m_context = context;
    [m_context retain];
    GLint sync = 0;
    [m_context setValues:&sync forParameter:NSOpenGLCPSwapInterval];
    return self;
}

- (void)dealloc
{
    motor_info(Motor::Log::gl(), "destroying OpenGL view");
    [m_context release];
    [super dealloc];
}

@end

namespace Motor { namespace OpenGL {

class GLRenderer::Context : public minitl::pointer
{
    friend class GLRenderer;
    friend class GLWindow;

private:
    NSOpenGLPixelFormat* m_pixelFormat;
    NSOpenGLContext*     m_context;
    ShaderExtensions     m_shaderext;

public:
    Context();
    ~Context() override;
};

static NSOpenGLPixelFormatAttribute s_attributes[] = {
    // NSOpenGLPFAAllRenderers,
    NSOpenGLPFADoubleBuffer,
    // NSOpenGLPFAWindow,
    NSOpenGLPFAAccelerated, NSOpenGLPFANoRecovery, NSOpenGLPFAMinimumPolicy, NSOpenGLPFAColorSize,
    (NSOpenGLPixelFormatAttribute)24, NSOpenGLPFAAlphaSize, (NSOpenGLPixelFormatAttribute)8,
    NSOpenGLPFADepthSize, (NSOpenGLPixelFormatAttribute)24, (NSOpenGLPixelFormatAttribute)0};

GLRenderer::Context::Context()
    : m_pixelFormat([[NSOpenGLPixelFormat alloc] initWithAttributes:s_attributes])
    , m_context([[NSOpenGLContext alloc] initWithFormat:m_pixelFormat shareContext:nil])
{
    GLint sync = 0;
    [m_context setValues:&sync forParameter:NSOpenGLCPSwapInterval];
    [m_context makeCurrentContext];
    motor_info_format(Motor::Log::gl(), "Created OpenGL context {0} ({1}) on {2}",
                      (const char*)glGetString(GL_VERSION), (const char*)glGetString(GL_VENDOR),
                      (const char*)glGetString(GL_RENDERER));
}

GLRenderer::Context::~Context()
{
    [m_context release];
    [m_pixelFormat release];
}

class GLWindow::Context : public minitl::pointer
{
    friend class GLRenderer;
    friend class GLWindow;

private:
    NSWindow*        m_window;
    MotorOpenGLView* m_view;
    CGLContextObj    m_context;
    u64              m_threadId;

public:
    Context(NSWindow* window, NSOpenGLContext* context, u64 threadId);
    ~Context() override;
};

GLWindow::Context::Context(NSWindow* window, NSOpenGLContext* context, u64 threadId)
    : m_window(window)
    , m_view([[MotorOpenGLView alloc]
          initWithFrame:[m_window contentRectForFrameRect:[m_window frame]]
                context:context])
    , m_context((CGLContextObj)[context CGLContextObj])
    , m_threadId(threadId)
{
    [window setContentView:m_view];
    [window makeKeyAndOrderFront:nil];
    [m_view->m_context setView:m_view];
}

GLWindow::Context::~Context()
{
    [m_window setContentView:nil];
    [m_view release];
}

//------------------------------------------------------------------------

GLRenderer::GLRenderer(const Plugin::Context& context)
    : Windowing::Renderer(Arena::general(), context.resourceManager)
    , m_context(scoped< Context >::create(Arena::general()))
    , m_openGLMemoryHost(scoped< GLMemoryHost >::create(Arena::general()))
    , m_openCLScheduler(inamespace("plugin.compute.opencl_gl"), context)
{
    [NSOpenGLContext clearCurrentContext];
}

GLRenderer::~GLRenderer()
{
    flush();
}

void GLRenderer::attachWindow(const weak< GLWindow >& w) const
{
    NSWindow*        window  = (NSWindow*)w->getWindowHandle();
    NSOpenGLContext* context = [[NSOpenGLContext alloc] initWithFormat:m_context->m_pixelFormat
                                                          shareContext:m_context->m_context];
    motor_assert(window, "No native window created for Motor window");
    w->m_context = scoped< GLWindow::Context >::create(Arena::general(), window, context,
                                                       Thread::currentId());
    [context release];
}

const ShaderExtensions& GLRenderer::shaderext() const
{
    motor_assert(m_context, "extensions required before context was created");
    return m_context->m_shaderext;
}

bool GLRenderer::success() const
{
    return hasPlatformRenderer() && m_context != 0;
}

//------------------------------------------------------------------------

GLWindow::GLWindow(const weak< const RenderWindowDescription >& windowDescription,
                   const weak< const GLRenderer >&              renderer)
    : Windowing::Window(windowDescription, renderer)
    , m_context(scoped< Context >())
{
}

void GLWindow::load(const weak< const Resource::IDescription >& windowDescription)
{
    Window::load(windowDescription);
    motor_checked_cast< const GLRenderer >(m_renderer)->attachWindow(this);
}

void GLWindow::unload()
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    Window::unload();
    m_context = scoped< Context >();
}

void GLWindow::setCurrent() const
{
    if(m_context)
    {
        motor_assert_format(
            Thread::currentId() == m_context->m_threadId,
            "render command on wrong thread: Window belongs to thread {0}, current thread: {1}",
            m_context->m_threadId, Thread::currentId());
        [m_context->m_view->m_context makeCurrentContext];
    }
}

void GLWindow::clearCurrent() const
{
    if(m_context)
    {
        motor_assert_format(
            Thread::currentId() == m_context->m_threadId,
            "render command on wrong thread: Window belongs to thread {0}, current thread: {1}",
            m_context->m_threadId, Thread::currentId());
        [NSOpenGLContext clearCurrentContext];
    }
}

void GLWindow::present() const
{
    if(m_context)
    {
        motor_assert_format(
            Thread::currentId() == m_context->m_threadId,
            "render command on wrong thread: Window belongs to thread {0}, current thread: {1}",
            m_context->m_threadId, Thread::currentId());
        CGLFlushDrawable(m_context->m_context);
    }
}

}}  // namespace Motor::OpenGL
