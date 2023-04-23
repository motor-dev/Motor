/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    GLSurface(const weak< const RenderSurfaceDescription >& surfaceDescription,
              const weak< GLRenderer >&                     renderer);
    ~GLSurface() override;

    void load(const weak< const Resource::IDescription >& surfaceDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::OpenGL
