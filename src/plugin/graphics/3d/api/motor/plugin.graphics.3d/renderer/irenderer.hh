/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_RENDERER_IRENDERER_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_RENDERER_IRENDERER_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor {

namespace Task {
class ITask;
}

namespace KernelScheduler {
class Kernel;
}

class RenderSurfaceDescription;
class RenderWindowDescription;
class MeshDescription;
class ShaderProgramDescription;
class TextureDescription;
class IGPUResource;
template < typename R >
class GPUResourceLoader;

class motor_api(3D) IRenderer : public minitl::pointer
{
    template < typename R >
    friend class GPUResourceLoader;

protected:
    minitl::allocator&                                      m_allocator;
    weak< Resource::ResourceManager >                       m_resourceManager;
    scoped< Task::ITask >                                   m_syncTask;
    scoped< GPUResourceLoader< RenderSurfaceDescription > > m_renderSurfaceLoader;
    scoped< GPUResourceLoader< RenderWindowDescription > >  m_renderWindowLoader;
    scoped< GPUResourceLoader< ShaderProgramDescription > > m_shaderProgramLoader;
    scoped< KernelScheduler::Kernel >                       m_kernelSort;
    scoped< KernelScheduler::Kernel >                       m_kernelRender;

protected:
    IRenderer(minitl::allocator & allocator, const weak< Resource::ResourceManager >& manager,
              Scheduler::Affinity affinity = Scheduler::WorkerThread);
    ~IRenderer() override;

protected:
    virtual void flush();

    virtual scoped< IGPUResource > create(weak< const RenderSurfaceDescription > rendertarget) const
        = 0;
    virtual scoped< IGPUResource > create(weak< const RenderWindowDescription > renderwindow) const
        = 0;
    // virtual ref<IGPUResource>   create(weak<const Mesh> mesh) const = 0;
    virtual scoped< IGPUResource > create(weak< const ShaderProgramDescription > shader) const = 0;
    // virtual ref<IGPUResource>   create(weak<const Texture> texture) = 0;
public:
    weak< IGPUResource > getRenderSurface(const weak< const Resource::IDescription >& description)
        const;
    weak< IGPUResource > getRenderWindow(const weak< const Resource::IDescription >& description)
        const;
    weak< IGPUResource > getShaderProgram(const weak< const Resource::IDescription >& description)
        const;

    minitl::allocator&  arena() const;
    weak< Task::ITask > syncTask() const;

    virtual knl::uint2 getScreenSize() const                   = 0;
    virtual u32        getMaxSimultaneousRenderTargets() const = 0;
};

}  // namespace Motor

#endif
