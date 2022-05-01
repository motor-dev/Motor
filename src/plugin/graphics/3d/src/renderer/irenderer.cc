/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/mesh/mesh.meta.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <motor/plugin.graphics.3d/texture/texture.meta.hh>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <motor/scheduler/task/method.hh>
#include <gpuresourceloader.hh>

namespace Motor {

IRenderer::IRenderer(minitl::Allocator& allocator, weak< Resource::ResourceManager > manager,
                     Scheduler::Affinity affinity)
    : m_allocator(allocator)
    , m_resourceManager(manager)
    , m_syncTask(ref< Task::Task< Task::MethodCaller< IRenderer, &IRenderer::flush > > >::create(
          Arena::task(), "flush", Colors::Red::Red,
          ref< Task::MethodCaller< IRenderer, &IRenderer::flush > >::create(Arena::task(), this),
          affinity))
    , m_renderSurfaceLoader(
          scoped< GPUResourceLoader< RenderSurfaceDescription > >::create(Arena::resource(), this))
    , m_renderWindowLoader(
          scoped< GPUResourceLoader< RenderWindowDescription > >::create(Arena::resource(), this))
    , m_shaderProgramLoader(
          scoped< GPUResourceLoader< ShaderProgramDescription > >::create(Arena::resource(), this))
//,   m_kernelSort(scoped<Kernel::KernelDescription>::create(Arena::task(),
//"graphics.3d.batchsort")) ,
// m_kernelRender(scoped<Kernel::KernelDescription>::create(Arena::task(),
//"graphics.3d.batchrender"))
{
    m_resourceManager->attach(motor_class< RenderSurfaceDescription >(), m_renderSurfaceLoader);
    m_resourceManager->attach(motor_class< RenderWindowDescription >(), m_renderWindowLoader);
    m_resourceManager->attach(motor_class< ShaderProgramDescription >(), m_shaderProgramLoader);
    // m_resourceManager->load(weak<Kernel::KernelDescription>(m_kernelSort));
    // m_resourceManager->load(weak<Kernel::KernelDescription>(m_kernelRender));
}

IRenderer::~IRenderer()
{
    // m_resourceManager->unload(weak<Kernel::KernelDescription>(m_kernelRender));
    // m_resourceManager->unload(weak<Kernel::KernelDescription>(m_kernelSort));
    m_resourceManager->detach(motor_class< ShaderProgramDescription >(), m_shaderProgramLoader);
    m_resourceManager->detach(motor_class< RenderWindowDescription >(), m_renderWindowLoader);
    m_resourceManager->detach(motor_class< RenderSurfaceDescription >(), m_renderSurfaceLoader);
}

weak< Task::ITask > IRenderer::syncTask() const
{
    return m_syncTask;
}

minitl::Allocator& IRenderer::arena() const
{
    return m_allocator;
}

void IRenderer::flush()
{
    m_renderSurfaceLoader->flush();
    m_renderWindowLoader->flush();
    m_shaderProgramLoader->flush();
}

weak< IGPUResource >
IRenderer::getRenderSurface(weak< const Resource::IDescription > description) const
{
    return description->getResource(m_renderSurfaceLoader).getRefHandle< IGPUResource >();
}

weak< IGPUResource >
IRenderer::getRenderWindow(weak< const Resource::IDescription > description) const
{
    return description->getResource(m_renderWindowLoader).getRefHandle< IGPUResource >();
}

weak< IGPUResource >
IRenderer::getShaderProgram(weak< const Resource::IDescription > description) const
{
    return description->getResource(m_shaderProgramLoader).getRefHandle< IGPUResource >();
}

}  // namespace Motor
