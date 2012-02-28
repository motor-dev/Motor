/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_WINDOWING_RENDERER_HH_
#define BE_WINDOWING_RENDERER_HH_
/*****************************************************************************/
#include    <3d/renderer/irenderer.hh>
#include    <windowing/window.hh>

namespace BugEngine { namespace Windowing
{

class Window;
struct WindowCreationFlags;

class Renderer : public IRenderer
{
    friend class Window;
    friend class Window::PlatformWindow;
    BE_NOCOPY(Renderer);
private:
    class PlatformRenderer;
    friend class PlatformRenderer;
    scoped<PlatformRenderer>    m_platformRenderer;
protected:
    void            flush() override;
protected:
    void*           createDummyHandle();
public:
    Renderer(Allocator& allocator, weak<ResourceManager> manager);
    ~Renderer();

    uint2           getScreenSize() override;
    void*           getPlatformData();
};

}}

/*****************************************************************************/
#endif