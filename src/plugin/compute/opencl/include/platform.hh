/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.opencl/stdafx.h>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Context;

class Platform : public minitl::refcountable
{
    friend class Context;

private:
    const cl_platform_id             m_platformId;
    minitl::vector< ref< Context > > m_contexts;

public:
    Platform(cl_platform_id platformId);
    ~Platform();

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
