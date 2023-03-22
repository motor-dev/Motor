/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_OPENCL_STDAFX_H_
#define MOTOR_COMPUTE_OPENCL_STDAFX_H_
/**************************************************************************************************/

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
        if(err != CL_SUCCESS)                                                                      \
            motor_error_format(Motor::Log::opencl(), "OpenCL call {0} failed with error code {1}", \
                               #a, err);                                                           \
    } while(0)

namespace Motor {

namespace KernelScheduler { namespace OpenCL {

struct CLStringInfo
{
    enum
    {
        InfoLogSize = 1024
    };
    char info[InfoLogSize];
};

}}  // namespace KernelScheduler::OpenCL

namespace Log {

motor_api(OPENCL) weak< Logger > opencl();

}

}  // namespace Motor

/**************************************************************************************************/
#endif
