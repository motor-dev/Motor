/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_opencl)
#    define MOTOR_API_OPENCL MOTOR_EXPORT
#elif defined(motor_dll_opencl)
#    define MOTOR_API_OPENCL MOTOR_IMPORT
#else
#    define MOTOR_API_OPENCL
#endif

#ifdef MOTOR_PLATFORM_MACOS
#    include <OpenCL/opencl.h>
#else
#    include <CL/cl.h>
#endif

#define checkResult(a)                                                                             \
    do                                                                                             \
    {                                                                                              \
        cl_int err = a;                                                                            \
        if(err != CL_SUCCESS) motor_error("OpenCL call %s failed with error code %d" | #a | err);  \
    } while(0)

namespace Motor { namespace KernelScheduler { namespace OpenCL {

struct CLStringInfo
{
    enum
    {
        InfoLogSize = 1024
    };
    char info[InfoLogSize];
};

}}}  // namespace Motor::KernelScheduler::OpenCL
