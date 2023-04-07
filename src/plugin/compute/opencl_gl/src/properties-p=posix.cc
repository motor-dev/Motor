/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <scheduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL_GL {

minitl::array< cl_context_properties > Scheduler::createPlatformSpecificContextProperties()
{
    motor_info(Log::opencl_gl(), "not implemented yet.");
    minitl::array< cl_context_properties > properties(Arena::temporary(), 1);
    properties[0] = 0;
    return properties;
}

}}}  // namespace Motor::KernelScheduler::OpenCL_GL
