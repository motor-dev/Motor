/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <scheduler.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL_GL {

minitl::vector< cl_context_properties > Scheduler::createPlatformSpecificContextProperties()
{
    HGLRC glrc = wglGetCurrentContext();
    HDC   dc   = wglGetCurrentDC();
    if(glrc)
    {
        minitl::vector< cl_context_properties > properties(Arena::temporary(), 5);
        properties[0] = CL_GL_CONTEXT_KHR;
        properties[1] = (cl_context_properties)glrc;
        properties[2] = CL_WGL_HDC_KHR;
        properties[3] = (cl_context_properties)dc;
        properties[4] = 0;
        return properties;
    }
    else
    {
        motor_info(Log::opencl_gl(),
                   "no OpenGL context found; OpenGL/OpenCL compatibility disabled");
        minitl::vector< cl_context_properties > properties(Arena::temporary(), 1);
        properties[0] = 0;
        return properties;
    }
}

}}}  // namespace Motor::KernelScheduler::OpenCL_GL
