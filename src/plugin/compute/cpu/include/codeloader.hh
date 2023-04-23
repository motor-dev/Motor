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
    explicit CodeLoader(const inamespace& cpuVariant);
    ~CodeLoader() override;

    void load(const weak< const Resource::IDescription >& codeDescription,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& scodeDescription,
                Resource::Resource&                         resource) override;
};

}}}  // namespace Motor::KernelScheduler::CPU
