/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <clkernelscheduler.hh>
#include    <clkernelloader.hh>
#include    <system/resource/resourcemanager.hh>
#include    <system/scheduler/scheduler.hh>
#include    <system/scheduler/kernel/kernel.script.hh>

namespace BugEngine
{

static void checkResult(cl_int err)
{
    if (err != CL_SUCCESS)
    {
        be_error("OpenCL error code %d" | err);
    }
}

static minitl::format<1024> getPlatformInfo(cl_platform_id platform, cl_platform_info name)
{
    minitl::format<1024> result("");
    size_t size = 0;
    checkResult(clGetPlatformInfo(platform, name, 0, 0, &size));
    char* temp = (char*)malloca(size+1);
    checkResult(clGetPlatformInfo(platform, name, size, temp, 0));
    result.append(temp);
    freea(temp);
    return result;
}

static minitl::format<1024> getDeviceInfo(cl_device_id device, cl_device_info name)
{
    minitl::format<1024> result("");
    size_t size = 0;
    checkResult(clGetDeviceInfo(device, name, 0, 0, &size));
    char* temp = (char*)malloca(size+1);
    checkResult(clGetDeviceInfo(device, name, size, temp, 0));
    result.append(temp);
    freea(temp);
    return result;
}

cl_context OpenCLKernelScheduler::createCLContext()
{
    cl_platform_id platform;

    cl_uint platformCount = 0;
    checkResult(clGetPlatformIDs(0, 0, &platformCount));
    cl_platform_id* platforms = (cl_platform_id*)malloca(sizeof(cl_platform_id)*platformCount);
    checkResult(clGetPlatformIDs(platformCount, platforms, &platformCount));
    for (cl_uint i = 0; i < platformCount; ++i)
    {
        cl_platform_id p = platforms[i];
        be_info("Found OpenCL platform %s (%s/%s)"
                |   getPlatformInfo(p, CL_PLATFORM_NAME)
                |   getPlatformInfo(p, CL_PLATFORM_VENDOR)
                |   getPlatformInfo(p, CL_PLATFORM_VERSION));
    }
    platform = platforms[0];
    freea(platforms);

    cl_device_id device;
    cl_uint deviceCount = 0;
    checkResult(clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU|CL_DEVICE_TYPE_ACCELERATOR, 0, 0, &deviceCount));
    cl_device_id* devices = (cl_device_id*)malloca(sizeof(cl_device_id) * deviceCount);
    checkResult(clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU|CL_DEVICE_TYPE_ACCELERATOR, deviceCount, devices, 0));

    for (cl_uint i = 0; i < deviceCount; ++i)
    {
        cl_device_id d = devices[i];
        be_info("Found %s %s on %s (%s/%s)"
                |   getDeviceInfo(d, CL_DEVICE_VERSION)
                |   getDeviceInfo(d, CL_DEVICE_PROFILE)
                |   getDeviceInfo(d, CL_DEVICE_NAME)
                |   getDeviceInfo(d, CL_DEVICE_VENDOR)
                |   getDeviceInfo(d, CL_DRIVER_VERSION));
    }
    device = devices[0];
    freea(devices);


    size_t size = 0;
    checkResult(clGetDeviceInfo(device, CL_DEVICE_EXTENSIONS, 0, 0, &size));
    char* deviceExtensions = (char*)malloca(size+1);
    deviceExtensions[size] = 0;
    checkResult(clGetDeviceInfo(device, CL_DEVICE_EXTENSIONS, size, deviceExtensions, 0));
    be_info("Extensions: %s" | deviceExtensions);
    freea(deviceExtensions);

    cl_context_properties contextProperties[256] = { 0 };
    fillPlatformSpecificContextProperties(deviceExtensions, contextProperties, 255);
    cl_int err;
    cl_context context = clCreateContext(0, 1, &device, 0, 0, &err);
    checkResult(err);

    return context;
}

OpenCLKernelScheduler::OpenCLKernelScheduler(const PluginContext& context)
    :   IKernelScheduler("OpenCL", context.scheduler)
    ,   m_resourceManager(context.resourceManager)
    ,   m_loader(scoped<OpenCLKernelLoader>::create(Arena::task()))
    ,   m_context(createCLContext())
{
    if (m_context)
    {
        m_resourceManager->attach<Kernel>(m_loader);
    }
}

OpenCLKernelScheduler::~OpenCLKernelScheduler()
{
    if (m_context)
    {
        m_resourceManager->detach<Kernel>(m_loader);
        clReleaseContext(m_context);
    }
}

}