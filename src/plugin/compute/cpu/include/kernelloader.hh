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
    explicit KernelLoader(const ref< CodeLoader >& codeLoader);
    ~KernelLoader() override;

    void load(const weak< const Resource::IDescription >& kernelDescription,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& kernelDescription,
                Resource::Resource&                         resource) override;
};

}}}  // namespace Motor::KernelScheduler::CPU
