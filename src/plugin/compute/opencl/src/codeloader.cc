/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/kernel.meta.hh>
#include <codeloader.hh>
#include <codeobject.hh>
#include <context.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

CodeLoader::CodeLoader(const weak< const Context >& context) : ICodeLoader(), m_context(context)
{
}

CodeLoader::~CodeLoader() = default;

void CodeLoader::load(const weak< const Resource::IDescription >& kernelDescription,
                      Resource::Resource&                         resource)
{
    motor_info_format(Log::opencl(), "loading OpenCL kernel code {0}",
                      motor_checked_cast< const Code >(kernelDescription)->name());
    inamespace name
        = motor_checked_cast< const Code >(kernelDescription)->name() + inamespace("cl");
    resource.setRefHandle(ref< CodeObject >::create(Arena::task(), m_context, name));
}

void CodeLoader::unload(const weak< const Resource::IDescription >& /*codeDescription*/,
                        Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::OpenCL
