/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <codeloader.hh>
#include <kernelobject.hh>
#include <motor/scheduler/kernel/kernel.script.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

CodeLoader::CodeLoader() : ICodeLoader()
{
}

CodeLoader::~CodeLoader()
{
}

void CodeLoader::load(weak< const Resource::Description > kernelDescription,
                      Resource::Resource&                 resource)
{
    motor_info("loading Cuda kernel %s"
               | motor_checked_cast< const Kernel >(kernelDescription)->name());
    inamespace name
        = motor_checked_cast< const Kernel >(kernelDescription)->name() + inamespace("cuda");
    resource.setRefHandle(ref< KernelObject >::create(Arena::task(), name));
}

void CodeLoader::reload(weak< const Resource::Description > /*oldKernelDescription*/,
                        weak< const Resource::Description > newKernelDescription,
                        Resource::Resource&                 resource)
{
    unload(resource);
    load(newKernelDescription, resource);
}

void CodeLoader::unload(Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::Cuda
