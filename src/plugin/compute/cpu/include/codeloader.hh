/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/icodeloader.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeLoader : public ICodeLoader
{
private:
    const inamespace m_cpuVariant;

public:
    CodeLoader(const inamespace& cpuVariant);
    ~CodeLoader();

    virtual void load(weak< const Resource::IDescription > codeDescription,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > scodeDescription,
                        Resource::Resource&                  resource) override;
};

}}}  // namespace Motor::KernelScheduler::CPU
