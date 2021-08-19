/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_LOADERS_RENDERTARGET_GLSURFACE_HH_
#define MOTOR_GL4_LOADERS_RENDERTARGET_GLSURFACE_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLSurface : public IRenderTarget
{
private:
    void setCurrent() const;
    void clearCurrent() const;

public:
    GLSurface(weak< const RenderSurfaceDescription > surfaceDescription,
              weak< GLRenderer >                     renderer);
    ~GLSurface();

    virtual void load(weak< const Resource::Description > surfaceDescription) override;
    virtual void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::OpenGL

/**************************************************************************************************/
#endif
