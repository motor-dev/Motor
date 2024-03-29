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

#include <GL4/wglext.h>

namespace Motor { namespace OpenGL {

static const PIXELFORMATDESCRIPTOR s_pfd
    = {sizeof(PIXELFORMATDESCRIPTOR),
       1,
       PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
       PFD_TYPE_RGBA,
       32,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       24,
       0,
       0,
       PFD_MAIN_PLANE,
       0,
       0,
       0,
       0};

class GLRenderer::Context : public minitl::pointer
{
    friend class GLRenderer;

private:
    HWND                      m_dummyHwnd;
    HDC                       m_dummyDC;
    HGLRC                     m_glContext;
    PFNWGLSWAPINTERVALEXTPROC m_setSwapInterval;
    u64                       m_threadId;

public:
    const ShaderExtensions shaderext;

public:
    explicit Context(const weak< const GLRenderer >& renderer);
    ~Context() override;
};

static HWND createDummyWnd(const weak< const GLRenderer >& renderer)
{
    minitl::format_buffer< 128u > classname
        = minitl::format< 128u >(FMT("__motor__{0}__"), (const void*)renderer);
    HWND hWnd = CreateWindowExA(0, classname.c_str(), "", WS_POPUP, 0, 0, 1, 1, nullptr, nullptr,
                                (HINSTANCE)::GetModuleHandle(nullptr), nullptr);
    if(!hWnd)
    {
        char* errorMessage;
        ::FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, nullptr,
                        ::GetLastError(), 0, reinterpret_cast< LPTSTR >(&errorMessage), 0, nullptr);
        motor_error(Log::gl(), errorMessage);
        ::LocalFree(errorMessage);
    }
    return hWnd;
}

static HGLRC createGLContext(const weak< const GLRenderer >& renderer, HDC hdc)
{
    auto pixelFormat = ChoosePixelFormat(hdc, &s_pfd);
    SetPixelFormat(hdc, pixelFormat, &s_pfd);

    PFNWGLCREATECONTEXTATTRIBSARBPROC wglCreateContextAttribsARB;

    {
        HWND hwnd = createDummyWnd(renderer);
        HDC  dc   = GetDC(hwnd);
        auto pf   = ChoosePixelFormat(hdc, &s_pfd);
        SetPixelFormat(dc, pf, &s_pfd);

        // phony context to get the context creation method
        HGLRC glrc = wglCreateContext(dc);
        wglMakeCurrent(dc, glrc);

        wglCreateContextAttribsARB = motor_function_cast< PFNWGLCREATECONTEXTATTRIBSARBPROC >(
            wglGetProcAddress("wglCreateContextAttribsARB"));

        wglMakeCurrent(nullptr, nullptr);
        wglDeleteContext(glrc);
        ReleaseDC(hwnd, dc);
        DestroyWindow(hwnd);
    }
    HGLRC rc = nullptr;
    if(wglCreateContextAttribsARB)
    {
        int attribs[] = {WGL_CONTEXT_MAJOR_VERSION_ARB,
                         4,
                         WGL_CONTEXT_MINOR_VERSION_ARB,
                         1,
                         WGL_CONTEXT_PROFILE_MASK_ARB,
                         WGL_CONTEXT_CORE_PROFILE_BIT_ARB,
                         WGL_CONTEXT_FLAGS_ARB,
                         WGL_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB,
                         0};
        rc            = wglCreateContextAttribsARB(hdc, nullptr, attribs);
        if(!rc)
        {
            attribs[1] = 3;
            attribs[3] = 2;
            rc         = wglCreateContextAttribsARB(hdc, nullptr, attribs);
        }
        if(!rc)
        {
            attribs[1] = 3;
            attribs[3] = 0;
            rc         = wglCreateContextAttribsARB(hdc, nullptr, attribs);
        }
        if(!rc)
        {
            attribs[1] = 2;
            attribs[3] = 0;
            rc         = wglCreateContextAttribsARB(hdc, nullptr, attribs);
        }
    }

    if(!rc)
    {
        rc = wglCreateContext(hdc);
    }

    if(rc)
    {
        wglMakeCurrent(hdc, rc);
        motor_info_format(Log::gl(), "Created OpenGL context {0} ({1}) on {2}",
                          (const char*)glGetString(GL_VERSION), (const char*)glGetString(GL_VENDOR),
                          (const char*)glGetString(GL_RENDERER));
    }
    else
    {
        motor_error(Log::gl(), "Could not create a GL context");
    }
    return rc;
}

GLRenderer::Context::Context(const weak< const GLRenderer >& renderer)
    : m_dummyHwnd(createDummyWnd(renderer))
    , m_dummyDC(GetDC(m_dummyHwnd))
    , m_glContext(createGLContext(renderer, m_dummyDC))
    , m_setSwapInterval(
          motor_function_cast< PFNWGLSWAPINTERVALEXTPROC >(wglGetProcAddress("wglSwapIntervalEXT")))
    , m_threadId(Thread::currentId())
    , shaderext()
{
    motor_forceuse(m_threadId);
}

GLRenderer::Context::~Context()
{
    wglMakeCurrent(nullptr, nullptr);
    if(m_glContext) wglDeleteContext(m_glContext);
    ReleaseDC(m_dummyHwnd, m_dummyDC);
    DestroyWindow(m_dummyHwnd);
}

class GLWindow::Context : public minitl::pointer
{
    friend class GLWindow;

private:
    HGLRC m_glContext;
    HWND  m_hwnd;
    HDC   m_dc;
    HDC   m_defaultDc;
    u64   m_threadId;

public:
    Context(HGLRC rc, HWND hwnd, HDC defaultDc, u64 threadId);
    ~Context() override;
};

GLWindow::Context::Context(HGLRC rc, HWND hwnd, HDC defaultDc, u64 threadId)
    : m_glContext(rc)
    , m_hwnd(hwnd)
    , m_dc(GetDC(hwnd))
    , m_defaultDc(defaultDc)
    , m_threadId(threadId)
{
    motor_forceuse(m_threadId);
    auto pixelFormat = ChoosePixelFormat(m_dc, &s_pfd);
    SetPixelFormat(m_dc, pixelFormat, &s_pfd);
}

GLWindow::Context::~Context()
{
    ReleaseDC(m_hwnd, m_dc);
    /*if (m_glContext)
    {
       wglDeleteContext(m_glContext);
        m_glContext = 0;
    }*/
}

//------------------------------------------------------------------------

GLRenderer::GLRenderer(const Plugin::Context& context)
    : Windowing::Renderer(Arena::general(), context.resourceManager)
    , m_context(scoped< Context >::create(Arena::general(), this))
    , m_openGLMemoryHost(scoped< GLMemoryHost >::create(Arena::general()))
    , m_openCLScheduler(inamespace("plugin.compute.opencl_gl"), context)
{
}

GLRenderer::~GLRenderer()
{
    flush();
}

void GLRenderer::attachWindow(const weak< GLWindow >& w) const
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    HWND wnd     = *(HWND*)w->getWindowHandle();
    w->m_context = scoped< GLWindow::Context >::create(
        Arena::general(), m_context->m_glContext, wnd, m_context->m_dummyDC, m_context->m_threadId);
    w->setCurrent();
    if(m_context->m_setSwapInterval) (*m_context->m_setSwapInterval)(0);
    w->clearCurrent();
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

GLWindow::GLWindow(const weak< const RenderWindowDescription >& windowDescription,
                   const weak< const GLRenderer >&              renderer)
    : Windowing::Window(windowDescription, renderer)
    , m_context(scoped< Context >())
{
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
    m_context = scoped< Context >();
}

void GLWindow::setCurrent() const
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    if(!wglMakeCurrent(m_context->m_dc, m_context->m_glContext))
    {
        char* errorMessage;
        ::FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, nullptr,
                        ::GetLastError(), 0, reinterpret_cast< LPTSTR >(&errorMessage), 0, nullptr);
        motor_error(Log::gl(), errorMessage);
        ::LocalFree(errorMessage);
    }
}

void GLWindow::clearCurrent() const
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    if(!wglMakeCurrent(m_context->m_defaultDc, m_context->m_glContext))
    {
        char* errorMessage;
        ::FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, nullptr,
                        ::GetLastError(), 0, reinterpret_cast< LPTSTR >(&errorMessage), 0, nullptr);
        motor_error(Log::gl(), errorMessage);
        ::LocalFree(errorMessage);
    }
}

void GLWindow::present() const
{
    motor_assert(Thread::currentId() == m_context->m_threadId, "render command on wrong thread");
    SwapBuffers(m_context->m_dc);
}

}}  // namespace Motor::OpenGL
