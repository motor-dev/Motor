/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_RENDERER_HH_
#define MOTOR_GL4_RENDERER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin/plugin.hh>

namespace Motor {

class RenderTargetDescription;
class RenderWindowDescription;
class MeshDescription;
class TextureDescription;
class ShaderProgramDescription;
class IKernelScheduler;

namespace OpenGL {

class GLMemoryHost;
class GLWindow;
struct ShaderExtensions;

class GLRenderer : public Windowing::Renderer
{
    friend class GLWindow;

private:
    class Context;
    scoped< Context >                  m_context;
    scoped< GLMemoryHost >             m_openGLMemoryHost;
    Plugin::Plugin< IKernelScheduler > m_openCLScheduler;

public:
    GLRenderer(const Plugin::Context& context);
    ~GLRenderer();

    u32 getMaxSimultaneousRenderTargets() const override
    {
        return 1;
    }

    void flush() override;

public:
    const ShaderExtensions& shaderext() const;
    bool                    success() const;

private:
    void attachWindow(weak< GLWindow > w) const;

private:
    ref< IGPUResource > create(weak< const RenderSurfaceDescription > rendersurface) const override;
    ref< IGPUResource > create(weak< const RenderWindowDescription > renderwindow) const override;
    ref< IGPUResource > create(weak< const ShaderProgramDescription > shader) const override;
};

}  // namespace OpenGL
}  // namespace Motor

/**************************************************************************************************/
#endif
