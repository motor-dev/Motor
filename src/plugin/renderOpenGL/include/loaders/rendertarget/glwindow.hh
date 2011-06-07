/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_OPENGL_LOADERS_RENDERTARGET_GLWINDOW_HH_
#define BE_OPENGL_LOADERS_RENDERTARGET_GLWINDOW_HH_
/*****************************************************************************/
#include    <graphics/renderer/irenderer.hh>


namespace BugEngine { namespace Graphics { namespace OpenGL
{

class Renderer;

class GLWindow : public Windowing::Window
{
    friend class Renderer;
private:
    class Context;
    scoped<Context> m_context;
private:
    void setCurrent() const;
    void clearCurrent() const;
    void present() const;
private:
    void load(weak<const Resource> resource) override;
    void unload() override;
public:
    virtual void    begin(ClearMode clear) const override;
    virtual void    end(PresentMode present) const override;
public:
    GLWindow(weak<const RenderWindow> renderwindow, weak<Renderer> renderer);
    ~GLWindow();
};

}}}

/*****************************************************************************/
#endif