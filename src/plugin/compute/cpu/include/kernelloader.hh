/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/kernel/ikernelloader.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeLoader;

class KernelLoader : public IKernelLoader
{
public:
    KernelLoader(ref< CodeLoader > codeLoader);
    ~KernelLoader();

    virtual void load(weak< const Resource::IDescription > kernelDescription,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > kernelDescription,
                        Resource::Resource&                  resource) override;
};

}}}  // namespace Motor::KernelScheduler::CPU
