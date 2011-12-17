/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_3D_RENDERER_GPURESOURCELOADER_HH_
#define BE_3D_RENDERER_GPURESOURCELOADER_HH_
/*****************************************************************************/

namespace BugEngine { namespace Graphics
{

class IRenderer;
class IGPUResource;

template< typename R >
class GPUResourceLoader : public IResourceLoader
{
    friend class IRenderer;
    BE_NOCOPY(GPUResourceLoader);
private:
    weak<const IRenderer>                   m_renderer;
    minitl::intrusive_list<IGPUResource>    m_resources;
    minitl::vector< ref<IGPUResource> >     m_deletedResources;
public:
    GPUResourceLoader(weak<const IRenderer> renderer);
    ~GPUResourceLoader();
protected:
    virtual ResourceHandle load(weak<const Resource> resource) override;
    virtual void unload(const ResourceHandle& handle) override;
    void flush();
};

}}

#include <gpuresourceloader.inl>

/*****************************************************************************/
#endif