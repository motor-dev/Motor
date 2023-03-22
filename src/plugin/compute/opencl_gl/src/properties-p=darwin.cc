/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <dlfcn.h>
#include <scheduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL_GL {

minitl::array< cl_context_properties > Scheduler::createPlatformSpecificContextProperties()
{
    CGLContextObj ctx = CGLGetCurrentContext();
    typedef CGLShareGroupObj (*t_CGLGetShareGroup)(CGLContextObj obj);
    t_CGLGetShareGroup b_CGLGetShareGroup
        = (t_CGLGetShareGroup)dlsym(RTLD_DEFAULT, "CGLGetShareGroup");
    if(!b_CGLGetShareGroup)
    {
        motor_warning(Log::opencl_gl(),
                      "CGLGetShareGroup not found; OpenGL/OpenCL compatibility disabled");
        minitl::array< cl_context_properties > properties(Arena::temporary(), 1);
        properties[0] = 0;
        return properties;
    }
    CGLShareGroupObj group = (*b_CGLGetShareGroup)(ctx);
    if(group)
    {
        minitl::array< cl_context_properties > properties(Arena::temporary(), 3);
        properties[0] = CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE;
        properties[1] = (cl_context_properties)group;
        properties[2] = 0;
        return properties;
    }
    motor_info(Log::opencl_gl(), "no OpenGL context found; OpenGL/OpenCL compatibility disabled");
    minitl::array< cl_context_properties > properties(Arena::temporary(), 1);
    properties[0] = 0;
    return properties;
}

}}}  // namespace Motor::KernelScheduler::OpenCL_GL
