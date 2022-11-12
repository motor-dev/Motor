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
    KernelLoader(ref< CodeLoader > codeLoader);
    ~KernelLoader();

    virtual void load(weak< const Resource::IDescription > kernelDescription,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > kernelDescription,
                        Resource::Resource&                  resource) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL
