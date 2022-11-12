/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor {

class IRenderer;
class IGPUResource;

template < typename R >
class GPUResourceLoader : public Resource::ILoader
{
    friend class IRenderer;
    MOTOR_NOCOPY(GPUResourceLoader);

private:
    weak< const IRenderer >                m_renderer;
    minitl::intrusive_list< IGPUResource > m_pending;
    minitl::intrusive_list< IGPUResource > m_resources;
    minitl::vector< weak< IGPUResource > > m_deleted;

public:
    GPUResourceLoader(weak< const IRenderer > renderer);
    ~GPUResourceLoader();

protected:
    virtual void load(weak< const Resource::IDescription > description,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > description,
                        Resource::Resource&                  handle) override;
    void         flush();
};

}  // namespace Motor

#include <gpuresourceloader.inl>
