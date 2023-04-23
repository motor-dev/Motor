/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/scheduler/kernel/icodeloader.hh>

namespace Motor { namespace KernelScheduler { namespace Cuda {

class CodeLoader : public ICodeLoader
{
public:
    CodeLoader();
    ~CodeLoader() override;

    void load(const weak< const Resource::IDescription >& codeDescription,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& codeDescription,
                Resource::Resource&                         resource) override;
};

}}}  // namespace Motor::KernelScheduler::Cuda
