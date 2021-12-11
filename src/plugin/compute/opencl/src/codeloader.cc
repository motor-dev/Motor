/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <codeobject.hh>
#include <context.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

CodeLoader::CodeLoader(weak< const Context > context) : ICodeLoader(), m_context(context)
{
}

CodeLoader::~CodeLoader()
{
}

void CodeLoader::load(weak< const Resource::IDescription > kernelDescription,
                      Resource::Resource&                  resource)
{
    motor_info("loading OpenCL kernel code %s"
               | motor_checked_cast< const Code >(kernelDescription)->name());
    inamespace name
        = motor_checked_cast< const Code >(kernelDescription)->name() + inamespace("cl");
    resource.setRefHandle(ref< CodeObject >::create(Arena::task(), m_context, name));
}

void CodeLoader::unload(weak< const Resource::IDescription > /*codeDescription*/,
                        Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::OpenCL
