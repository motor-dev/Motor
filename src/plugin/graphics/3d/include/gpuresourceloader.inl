/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_RENDERER_GPURESOURCELOADER_INL_
#define MOTOR_3D_RENDERER_GPURESOURCELOADER_INL_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <gpuresourceloader.hh>

namespace Motor {

template < typename R >
GPUResourceLoader< R >::GPUResourceLoader(weak< const IRenderer > renderer)
    : m_renderer(renderer)
    , m_deleted(Arena::resource())
{
}

template < typename R >
GPUResourceLoader< R >::~GPUResourceLoader()
{
}

template < typename R >
void GPUResourceLoader< R >::load(weak< const Resource::IDescription > description,
                                  Resource::Resource&                  resource)
{
    ref< IGPUResource > handle = m_renderer->create(motor_checked_cast< const R >(description));
    resource.setRefHandle(handle);
    m_pending.push_back(*handle.operator->());
}

template < typename R >
void GPUResourceLoader< R >::unload(weak< const Resource::IDescription > /*description*/,
                                    Resource::Resource& resource)
{
    weak< IGPUResource > gpuResource = resource.getRefHandle< IGPUResource >();
    gpuResource->m_resource.clear();
    gpuResource->addref();
    m_deleted.push_back(gpuResource);
    resource.clearRefHandle();
}

template < typename R >
void GPUResourceLoader< R >::flush()
{
    while(!m_deleted.empty())
    {
        IGPUResource* resource = m_deleted.back().operator->();
        m_deleted.pop_back();
        resource->unload();
        resource->decref();
    }
    for(minitl::intrusive_list< IGPUResource >::iterator it = m_pending.begin();
        it != m_pending.end();)
    {
        IGPUResource& resource = *it;
        resource.load(resource.m_resource);
        it = m_pending.erase(it);
        m_resources.push_back(resource);
    }
}

}  // namespace Motor

/**************************************************************************************************/
#endif
