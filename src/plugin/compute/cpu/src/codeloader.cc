/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/code.meta.hh>
#include <codeloader.hh>
#include <codeobject.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

CodeLoader::CodeLoader(const inamespace& cpuVariant)
    : ICodeLoader()
    , m_cpuVariant(inamespace("cpu") + cpuVariant)
{
}

CodeLoader::~CodeLoader()
{
}

void CodeLoader::load(weak< const Resource::IDescription > codeDescription,
                      Resource::Resource&                  resource)
{
    motor_info("loading CPU kernel %s" | motor_checked_cast< const Code >(codeDescription)->name());
    inamespace name = motor_checked_cast< const Code >(codeDescription)->name();
    name += m_cpuVariant;
    resource.setRefHandle(ref< CodeObject >::create(Arena::task(), name));
}

void CodeLoader::unload(weak< const Resource::IDescription > /*codeDescription*/,
                        Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}}  // namespace Motor::KernelScheduler::CPU
