/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <context.hh>
#include <platform.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

static CLStringInfo getDeviceInfo(cl_device_id device, cl_device_info name)
{
    CLStringInfo result {};
    size_t       size = CLStringInfo::InfoLogSize;
    checkResult(clGetDeviceInfo(device, name, size, result.info, nullptr));
    return result;
}

static u32 getDevicePointerSize(cl_device_id device)
{
    u32 result;
    checkResult(clGetDeviceInfo(device, CL_DEVICE_ADDRESS_BITS, sizeof(result), &result, nullptr));
    return result;
}

Context::Context(const weak< Platform >& platform, cl_device_id device, cl_context context)
    : m_platform(platform)
    , m_device(device)
    , m_context(context)
    , m_pointerSize(getDevicePointerSize(device))
{
    motor_info_format(Log::opencl(), "Found {0} {1} on {2} ({3}/{4})",
                      getDeviceInfo(m_device, CL_DEVICE_VERSION).info,
                      getDeviceInfo(m_device, CL_DEVICE_PROFILE).info,
                      getDeviceInfo(m_device, CL_DEVICE_NAME).info,
                      getDeviceInfo(m_device, CL_DEVICE_VENDOR).info,
                      getDeviceInfo(m_device, CL_DRIVER_VERSION).info);
    size_t size = 0;
    checkResult(clGetDeviceInfo(m_device, CL_DEVICE_EXTENSIONS, 0, nullptr, &size));

    char* deviceExtensions         = (char*)malloca(size + 1);
    char* deviceExtensionsIterator = deviceExtensions;
    deviceExtensions[size]         = 0;
    checkResult(clGetDeviceInfo(m_device, CL_DEVICE_EXTENSIONS, size, deviceExtensions, nullptr));
    while(size > 100)
    {
        char* nextLine = deviceExtensionsIterator + 100;
        size -= 100;
        while(*nextLine != ' ')
        {
            nextLine--;
            size++;
        }
        *nextLine = 0;
        motor_info_format(Log::opencl(), "Extensions: {0}", deviceExtensionsIterator);
        deviceExtensionsIterator = nextLine + 1;
    }
    if(*deviceExtensionsIterator)
        motor_info_format(Log::opencl(), "Extensions: {0}", deviceExtensionsIterator);
    freea(deviceExtensions);
}

Context::~Context()
{
    clReleaseContext(m_context);
}

cl_program Context::buildProgram(u64 size, const char* code) const
{
    auto       codeSize  = motor_checked_numcast< size_t >(size);
    cl_int     errorCode = 0;
    cl_program program   = clCreateProgramWithSource(m_context, 1, &code, &codeSize, &errorCode);
    if(errorCode != CL_SUCCESS)
    {
        motor_error_format(
            Log::opencl(),
            "failed to load OpenCL kernel: clCreateProgramWithBinary failed with code {0}",
            errorCode);
        return program;
    }

    errorCode = clBuildProgram(program, 1, &m_device, "", nullptr, nullptr);
    cl_program_build_info info;
    size_t                len = 0;
    clGetProgramBuildInfo(program, m_device, CL_PROGRAM_BUILD_STATUS, sizeof(info), &info, &len);
    clGetProgramBuildInfo(program, m_device, CL_PROGRAM_BUILD_LOG, 0, nullptr, &len);
    if(len > 2)
    {
        minitl::allocator::block< char > buffer(Arena::temporary(), len + 1);
        clGetProgramBuildInfo(program, m_device, CL_PROGRAM_BUILD_LOG, (len + 1), buffer.data(),
                              &len);
        motor_info_format(Log::opencl(), "compilation result:\n{0}", buffer.data());
    }
    if(errorCode != CL_SUCCESS)
    {
        motor_error_format(Log::opencl(),
                           "failed to load OpenCL kernel: clBuildProgram failed with code {0}",
                           errorCode);
        return program;
    }
#if CL_VERSION_1_2
    {
        checkResult(clGetProgramInfo(program, CL_PROGRAM_KERNEL_NAMES, 0, nullptr, &len));
        minitl::allocator::block< char > buffer(Arena::temporary(), len + 1);
        clGetProgramInfo(program, CL_PROGRAM_KERNEL_NAMES, (len + 1), buffer.data(), &len);
        motor_info_format(Log::opencl(), "list of kernels: {0}", buffer.data());
        freea(buffer);
    }
#endif
    /*kernel = clCreateKernel(program, "_kmain", &errorCode);
    if(errorCode != CL_SUCCESS)
    {
        motor_error_format(Log::opencl(), "failed to load OpenCL kernel: clCreateKernel failed with
    code {0}", errorCode); return minitl::make_tuple(kernel, program);
    }
    else
    {
        motor_info(Log::opencl(), "success");
    }*/
    return program;
}

}}}  // namespace Motor::KernelScheduler::OpenCL
