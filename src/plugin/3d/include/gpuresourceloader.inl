/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_3D_RENDERER_GPURESOURCELOADER_INL_
#define BE_3D_RENDERER_GPURESOURCELOADER_INL_
/*****************************************************************************/
#include    <3d/renderer/igpuresource.hh>

namespace BugEngine { namespace Graphics
{

template< typename R >
GPUResourceLoader<R>::GPUResourceLoader(weak<const IRenderer> renderer)
    :   m_renderer(renderer)
    ,   m_deleted(gameArena())
{
}


template< typename R >
GPUResourceLoader<R>::~GPUResourceLoader()
{
}

template< typename R >
ResourceHandle GPUResourceLoader<R>::load(weak<const Resource> resource)
{
    ResourceHandle r;
    ref<IGPUResource> handle = m_renderer->create(be_checked_cast<const R>(resource));
    r.handle = handle;
    m_pending.push_back(*handle.operator->());
    return r;
}

template< typename R >
void GPUResourceLoader<R>::unload(const ResourceHandle& handle)
{
    be_checked_cast<IGPUResource>(handle.handle)->m_resource.clear();
    m_deleted.push_back(be_checked_cast<IGPUResource>(handle.handle));
}

template< typename R >
void GPUResourceLoader<R>::flush()
{
    m_deleted.clear();
    for (minitl::intrusive_list<IGPUResource>::iterator it = m_pending.begin(); it != m_pending.end(); )
    {
        IGPUResource& resource = *it;
        resource.load(resource.m_resource);
        it = m_pending.erase(it);
        m_resources.push_back(resource);
    }
}

}}

/*****************************************************************************/
#endif

