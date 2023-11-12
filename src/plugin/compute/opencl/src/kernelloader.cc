/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <kernelloader.hh>

#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <codeobject.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

KernelLoader::KernelLoader(const ref< CodeLoader >& codeLoader) : IKernelLoader(codeLoader)
{
}

KernelLoader::~KernelLoader() = default;

void KernelLoader::load(const weak< const Resource::IDescription >& kernelDescription,
                        Resource::Resource&                         resource)
{
    weak< const Kernel > kernel = motor_checked_cast< const Kernel >(kernelDescription);
    motor_info_format(Log::opencl(), "loading OpenCL kernel {0}", kernel->name());
    weak< CodeObject > code = kernel->code()->getResource(m_codeLoader).getHandle< CodeObject >();
    resource.setHandle(scoped< KernelObject >::create(Arena::task(), code, kernel->name()));
}

void KernelLoader::unload(const weak< const Resource::IDescription >& /*kernelDescription*/,
                          Resource::Resource& resource)
{
    resource.clearHandle();
}

}}}  // namespace Motor::KernelScheduler::OpenCL
