/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_GPURESOURCELOADER_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_GPURESOURCELOADER_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor {

class IRenderer;
class IGPUResource;

template < typename R >
class GPUResourceLoader : public Resource::ILoader
{
    friend class IRenderer;

private:
    weak< const IRenderer >                m_renderer;
    minitl::intrusive_list< IGPUResource > m_pending;
    minitl::intrusive_list< IGPUResource > m_resources;
    minitl::vector< weak< IGPUResource > > m_deleted;

public:
    explicit GPUResourceLoader(const weak< const IRenderer >& renderer);
    ~GPUResourceLoader() override;

protected:
    void load(const weak< const Resource::IDescription >& description,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         resource) override;
    void flush();
};

}  // namespace Motor

#include <gpuresourceloader.inl>

#endif
