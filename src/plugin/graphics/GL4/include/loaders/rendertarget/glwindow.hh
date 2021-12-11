/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_LOADERS_RENDERTARGET_GLWINDOW_HH_
#define MOTOR_GL4_LOADERS_RENDERTARGET_GLWINDOW_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLWindow : public Windowing::Window
{
    friend class GLRenderer;
    MOTOR_NOCOPY(GLWindow);

private:
    class Context;
    scoped< Context > m_context;

private:
    void setCurrent() const;
    void clearCurrent() const;
    void present() const;

private:
    void load(weak< const Resource::IDescription > windowDescription) override;
    void unload() override;

public:
    virtual void begin(ClearMode clear) const override;
    virtual void end(PresentMode present) const override;

public:
    GLWindow(weak< const RenderWindowDescription > windowDescription,
             weak< const GLRenderer >              renderer);
    ~GLWindow();
};

}}  // namespace Motor::OpenGL

/**************************************************************************************************/
#endif
