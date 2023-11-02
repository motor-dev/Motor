/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <kernelobject.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

CodeLoader::CodeLoader() : ICodeLoader()
{
}

CodeLoader::~CodeLoader() = default;

void CodeLoader::load(const weak< const Resource::IDescription >& kernelDescription,
                      Resource::Resource&                         resource)
{
    motor_info_format(Log::cuda(), "loading Cuda kernel {0}",
                      motor_checked_cast< const Kernel >(kernelDescription)->name());
    inamespace name
        = motor_checked_cast< const Kernel >(kernelDescription)->name() + inamespace("cuda");
    resource.setRefHandle(ref< KernelObject >::create(Arena::task(), name));
}

void CodeLoader::unload(const weak< const Resource::IDescription >& /*kernelDescription*/,
                        Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::Cuda
