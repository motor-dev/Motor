/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_RENDERER_IGPURESOURCE_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_RENDERER_IGPURESOURCE_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/resource/idescription.meta.hh>

namespace Motor {

namespace Resource {

class IDescription;

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

protected:
    const weak< const IRenderer >        m_renderer;
    weak< const Resource::IDescription > m_resource;

private:
    i32 m_index;

public:
    IGPUResource(const weak< const Resource::IDescription >& description,
                 const weak< const IRenderer >&              renderer);
    ~IGPUResource() override;

    virtual void load(const weak< const Resource::IDescription >& description) = 0;
    virtual void unload()                                                      = 0;

    weak< const Resource::IDescription > resource() const
    {
        return m_resource;
    }
};

}  // namespace Motor

#endif
