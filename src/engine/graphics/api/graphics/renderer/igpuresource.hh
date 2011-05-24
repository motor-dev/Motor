/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_GRAPHICS_RENDERER_IGPURESOURCE_HH_
#define BE_GRAPHICS_RENDERER_IGPURESOURCE_HH_
/*****************************************************************************/

namespace BugEngine { class Resource; }

namespace BugEngine { namespace Graphics
{

class IRenderer;
class GPUResourceLoader;

class be_api(GRAPHICS) IGPUResource :   public minitl::refcountable
                                    ,   public minitl::inode
                                    ,   public minitl::intrusive_list<IGPUResource>::item
{
    friend class GPUResourceLoader;
protected:
    const weak<const Resource>  m_resource;
    const weak<IRenderer>       m_renderer;
    mutable i32                 m_index;
public:
    IGPUResource(weak<const Resource> resource, weak<const IRenderer> renderer);
    virtual ~IGPUResource();

    virtual void load() = 0;
    virtual void unload() = 0;
};

}}

/*****************************************************************************/
#endif
