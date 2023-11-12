/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/plugin.compute.opencl/scheduler.hh>
#include <motor/plugin/plugin.hh>
#include <context.hh>
#include <platform.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class PlatformLoader : public minitl::pointer
{
private:
    minitl::vector< ref< Platform > >  m_platforms;
    minitl::vector< ref< Scheduler > > m_schedulers;

public:
    explicit PlatformLoader(const Plugin::Context& context);
    ~PlatformLoader() override;
};

PlatformLoader::PlatformLoader(const Plugin::Context& context)
    : m_platforms(Platform::loadPlatforms())
    , m_schedulers(Arena::task())
{
    for(minitl::vector< ref< Platform > >::const_iterator it = m_platforms.begin();
        it != m_platforms.end(); ++it)
    {
        for(minitl::vector< ref< Context > >::const_iterator ctxIt = (*it)->contextBegin();
            ctxIt != (*it)->contextEnd(); ++ctxIt)
        {
            m_schedulers.push_back(ref< Scheduler >::create(Arena::task(), context, *ctxIt));
        }
    }
}

PlatformLoader::~PlatformLoader() = default;

}}}  // namespace Motor::KernelScheduler::OpenCL

MOTOR_PLUGIN_REGISTER(Motor::KernelScheduler::OpenCL::PlatformLoader)
