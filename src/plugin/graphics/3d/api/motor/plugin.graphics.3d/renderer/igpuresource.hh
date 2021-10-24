/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_RENDERER_IGPURESOURCE_HH_
#define MOTOR_3D_RENDERER_IGPURESOURCE_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/refcountable.hh>

namespace Motor {

namespace Resource {
class Description;
}

template < typename R >
class GPUResourceLoader;
class IRenderer;

class motor_api(3D) IGPUResource
    : public minitl::refcountable
    , public minitl::intrusive_list< IGPUResource >::item
{
    template < typename T >
    friend class GPUResourceLoader;
    MOTOR_NOCOPY(IGPUResource);

protected:
    const weak< const IRenderer >       m_renderer;
    weak< const Resource::Description > m_resource;

private:
    i32 m_index;

public:
    IGPUResource(weak< const Resource::Description > description, weak< const IRenderer > renderer);
    virtual ~IGPUResource();

    virtual void load(weak< const Resource::Description > description) = 0;
    virtual void unload()                                              = 0;

    weak< const Resource::Description > resource() const
    {
        return m_resource;
    }
};

}  // namespace Motor

/**************************************************************************************************/
#endif