/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_OPENCL_PLATFORM_HH
#define MOTOR_PLUGIN_COMPUTE_OPENCL_PLATFORM_HH

#include <motor/plugin.compute.opencl/stdafx.h>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Context;

class Platform : public minitl::pointer
{
    friend class Context;

private:
    cl_platform_id                   m_platformId;
    minitl::vector< ref< Context > > m_contexts;

public:
    explicit Platform(cl_platform_id platformId);
    ~Platform() override;

public:
    static minitl::vector< ref< Platform > >         loadPlatforms();
    minitl::vector< ref< Context > >::const_iterator contextBegin()
    {
        return m_contexts.begin();
    }
    minitl::vector< ref< Context > >::const_iterator contextEnd()
    {
        return m_contexts.end();
    }
};
}}}  // namespace Motor::KernelScheduler::OpenCL

#endif
