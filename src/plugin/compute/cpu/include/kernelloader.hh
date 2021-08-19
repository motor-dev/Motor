/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CPU_KERNELLOADER_HH_
#define MOTOR_COMPUTE_CPU_KERNELLOADER_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/ikernelloader.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeLoader;

class KernelLoader : public IKernelLoader
{
public:
    KernelLoader(ref< CodeLoader > codeLoader);
    ~KernelLoader();

    virtual void load(weak< const Resource::Description > kernelDescription,
                      Resource::Resource&                 resource) override;
    virtual void reload(weak< const Resource::Description > oldKernelDescription,
                        weak< const Resource::Description > newKernelDescription,
                        Resource::Resource&                 resource) override;
    virtual void unload(Resource::Resource& resource) override;
};

}}}  // namespace Motor::KernelScheduler::CPU

/**************************************************************************************************/
#endif
