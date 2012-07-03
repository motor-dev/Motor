/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <kernelobject.hh>
#include    <system/plugin.hh>


namespace BugEngine
{

#ifndef BE_STATIC

void* KernelObject::loadKernel(const inamespace& kernel)
{
    minitl::format<> kernelFile = minitl::format<>(PLUGIN_PREFIX "%s" PLUGIN_EXT) | kernel;
    const ipath& kernelDirectory = Environment::getEnvironment().getDataDirectory();
    static const ipath kernelSubDirectory = ipath("kernels");
    minitl::format<ifilename::MaxFilenameLength> kernelPath = (kernelDirectory + kernelSubDirectory + ifilename(kernelFile.c_str())).str();
    be_info("loading kernel %s (%s)" | kernel | kernelPath);
    void* handle = dlopen(kernelPath.c_str(), RTLD_NOW|RTLD_LOCAL);
    if (!handle)
    {
        be_error(dlerror());
    }
    return handle;
}

void* KernelObject::loadSymbol(void* handle, const char *name)
{
    void* s = dlsym(handle, name);
    if (!s)
    {
        be_error(dlerror());
    }
    return s;
}

void KernelObject::unloadKernel(void* handle)
{
    dlclose(handle);
}

#endif

}