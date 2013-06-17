/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_KERNEL_OPENCL_CLKERNELLOADER_HH_
#define BE_KERNEL_OPENCL_CLKERNELLOADER_HH_
/*****************************************************************************/
#include    <scheduler/kernel/ikernelloader.hh>


namespace BugEngine
{

class OpenCLKernelLoader : public Kernel::IKernelLoader
{
public:
    OpenCLKernelLoader();
    ~OpenCLKernelLoader();

    virtual void load(weak<const Resource::Description> kernelDescription, Resource::Resource& resource) override;
    virtual void reload(weak<const Resource::Description> oldKernelDescription,
                        weak<const Resource::Description> newKernelDescription,
                         Resource::Resource& resource) override;
    virtual void unload(Resource::Resource& resource) override;
};

}


/*****************************************************************************/
#endif
