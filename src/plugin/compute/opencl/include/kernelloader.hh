/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/ikernelloader.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

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

}}}  // namespace Motor::KernelScheduler::OpenCL
