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
    ~CodeLoader();

    virtual void load(weak< const Resource::IDescription > codeDescription,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > codeDescription,
                        Resource::Resource&                  resource) override;
};

}}}  // namespace Motor::KernelScheduler::Cuda
