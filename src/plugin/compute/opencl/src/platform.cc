/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <context.hh>
#include <platform.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

static CLStringInfo getPlatformInfo(cl_platform_id platform, cl_platform_info name)
{
    CLStringInfo result {};
    size_t       size = CLStringInfo::InfoLogSize;
    checkResult(clGetPlatformInfo(platform, name, size, result.info, nullptr));
    return result;
}

minitl::vector< scoped< Platform > > Platform::loadPlatforms()
{
    minitl::vector< scoped< Platform > > result(Arena::task());
    cl_uint                              platformCount = 0;
    checkResult(clGetPlatformIDs(0, nullptr, &platformCount));
    if(platformCount)
    {
        result.reserve(platformCount);

        auto* platforms = (cl_platform_id*)malloca(sizeof(cl_platform_id) * platformCount);
        checkResult(clGetPlatformIDs(platformCount, platforms, &platformCount));
        for(cl_uint i = 0; i < platformCount; ++i)
        {
            cl_platform_id p = platforms[i];
            result.emplace_back(scoped< Platform >::create(Arena::task(), p));
        }
        freea(platforms);
    }
    return result;
}

Platform::Platform(cl_platform_id platformId) : m_platformId(platformId), m_contexts(Arena::task())
{
    motor_info_format(Log::opencl(), "Found OpenCL platform {0} ({1}/{2})",
                      getPlatformInfo(m_platformId, CL_PLATFORM_NAME).info,
                      getPlatformInfo(m_platformId, CL_PLATFORM_VENDOR).info,
                      getPlatformInfo(m_platformId, CL_PLATFORM_VERSION).info);

    cl_uint deviceCount = 0;
    cl_uint deviceType  = CL_DEVICE_TYPE_ACCELERATOR | CL_DEVICE_TYPE_GPU;
    cl_int  error       = clGetDeviceIDs(m_platformId, deviceType, 0, nullptr, &deviceCount);
    if(error != CL_DEVICE_NOT_FOUND)
    {
        if(error != CL_SUCCESS)
        {
            motor_error_format(Log::opencl(), "clGetDevice returned error code {0}", error);
        }
        else if(deviceCount > 0)
        {
            auto* devices = (cl_device_id*)malloca(sizeof(cl_device_id) * deviceCount);

            checkResult(clGetDeviceIDs(m_platformId, deviceType, deviceCount, devices, nullptr));
            for(cl_uint i = 0; i < deviceCount; ++i)
            {
                cl_device_id device = devices[i];
                cl_int       err;
                cl_context   context = clCreateContext(nullptr, 1, &device, nullptr, nullptr, &err);
                if(err != CL_SUCCESS)
                {
                    char   deviceName[1024];
                    size_t result;
                    clGetDeviceInfo(device, CL_DEVICE_NAME, sizeof(deviceName), deviceName,
                                    &result);
                    if(result >= sizeof(deviceName)) deviceName[sizeof(deviceName) - 1] = 0;
                    motor_error_format(Log::opencl(), "unable to create context for device {0}",
                                       deviceName);
                }
                else
                {
                    m_contexts.push_back(
                        scoped< Context >::create(Arena::task(), this, device, context));
                }
            }
            freea(devices);
        }
    }
}

Platform::~Platform() = default;

}}}  // namespace Motor::KernelScheduler::OpenCL
