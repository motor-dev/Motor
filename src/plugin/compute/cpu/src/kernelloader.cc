/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <codeobject.hh>

#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <kernelloader.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

KernelLoader::KernelLoader(scoped< CodeLoader >&& codeLoader)
    : IKernelLoader(minitl::move(codeLoader))
{
}

KernelLoader::~KernelLoader() = default;

void KernelLoader::load(const weak< const Resource::IDescription >& kernelDescription,
                        Resource::Resource&                         resource)
{
    weak< const Kernel > kernel = motor_checked_cast< const Kernel >(kernelDescription);
    weak< CodeObject >   code = kernel->code()->getResource(m_codeLoader).getHandle< CodeObject >();
    resource.setHandle(scoped< KernelObject >::create(Arena::task(), code, kernel->name()));
}

void KernelLoader::unload(const weak< const Resource::IDescription >& /*kernelDescription*/,
                          Resource::Resource& resource)
{
    resource.clearHandle();
}

}}}  // namespace Motor::KernelScheduler::CPU
