/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <scheduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL_GL {

Scheduler::Scheduler(const Plugin::Context& context)
    : OpenCL::Scheduler(context, &createPlatformSpecificContextProperties()[0])
{
}

Scheduler::~Scheduler()
{
}

}}}  // namespace Motor::KernelScheduler::OpenCL_GL
