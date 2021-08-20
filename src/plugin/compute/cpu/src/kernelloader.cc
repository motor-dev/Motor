/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <codeobject.hh>

#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <kernelloader.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

KernelLoader::KernelLoader(ref< CodeLoader > codeLoader) : IKernelLoader(codeLoader)
{
}

KernelLoader::~KernelLoader()
{
}

void KernelLoader::load(weak< const Resource::Description > kernelDescription,
                        Resource::Resource&                 resource)
{
    weak< const Kernel > kernel = motor_checked_cast< const Kernel >(kernelDescription);
    weak< CodeObject >   code
        = kernel->code()->getResource(m_codeLoader).getRefHandle< CodeObject >();
    resource.setRefHandle(ref< KernelObject >::create(Arena::task(), code, kernel->name()));
}

void KernelLoader::reload(weak< const Resource::Description > /*oldKernelDescription*/,
                          weak< const Resource::Description > newKernelDescription,
                          Resource::Resource&                 resource)
{
    unload(resource);
    load(newKernelDescription, resource);
}

void KernelLoader::unload(Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::CPU
