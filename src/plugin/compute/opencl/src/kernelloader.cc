/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <kernelloader.hh>

#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <codeobject.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

KernelLoader::KernelLoader(ref< CodeLoader > codeLoader) : IKernelLoader(codeLoader)
{
}

KernelLoader::~KernelLoader()
{
}

void KernelLoader::load(weak< const Resource::IDescription > kernelDescription,
                        Resource::Resource&                  resource)
{
    weak< const Kernel > kernel = motor_checked_cast< const Kernel >(kernelDescription);
    motor_info("loading OpenCL kernel %s" | kernel->name());
    weak< CodeObject > code
        = kernel->code()->getResource(m_codeLoader).getRefHandle< CodeObject >();
    resource.setRefHandle(ref< KernelObject >::create(Arena::task(), code, kernel->name()));
}

void KernelLoader::unload(weak< const Resource::IDescription > /*kernelDescription*/,
                          Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::OpenCL
