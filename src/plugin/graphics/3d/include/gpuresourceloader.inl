/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_GPURESOURCELOADER_INL
#define MOTOR_PLUGIN_GRAPHICS_3D_GPURESOURCELOADER_INL
#pragma once

#include <gpuresourceloader.hh>

#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>

namespace Motor {

template < typename R >
GPUResourceLoader< R >::GPUResourceLoader(const weak< const IRenderer >& renderer)
    : m_renderer(renderer)
    , m_deleted(Arena::resource())
{
}

template < typename R >
GPUResourceLoader< R >::~GPUResourceLoader() = default;

template < typename R >
void GPUResourceLoader< R >::load(const weak< const Resource::IDescription >& description,
                                  Resource::Resource&                         resource)
{
    scoped< IGPUResource > handle = m_renderer->create(motor_checked_cast< const R >(description));
    m_pending.push_back(*handle.operator->());
    resource.setHandle(minitl::move(handle));
}

template < typename R >
void GPUResourceLoader< R >::unload(const weak< const Resource::IDescription >& description,
                                    Resource::Resource&                         resource)
{
    motor_forceuse(description);
    scoped< IGPUResource > gpuResource = resource.stealHandle< IGPUResource >();
    gpuResource->m_resource.clear();
    m_deleted.push_back(minitl::move(gpuResource));
}

template < typename R >
void GPUResourceLoader< R >::flush()
{
    while(!m_deleted.empty())
    {
        m_deleted.back()->unload();
        m_deleted.pop_back();
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

#endif
