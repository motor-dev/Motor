/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLWindow : public Windowing::Window
{
    friend class GLRenderer;

private:
    class Context;
    scoped< Context > m_context;

private:
    void setCurrent() const;
    void clearCurrent() const;
    void present() const;

private:
    void load(const weak< const Resource::IDescription >& windowDescription) override;
    void unload() override;

public:
    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

public:
    GLWindow(const weak< const RenderWindowDescription >& windowDescription,
             const weak< const GLRenderer >&              renderer);
    ~GLWindow() override = default;
};

}}  // namespace Motor::OpenGL
