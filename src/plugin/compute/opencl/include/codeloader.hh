/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.compute.opencl/stdafx.h>
#include <motor/scheduler/kernel/icodeloader.hh>

namespace Motor { namespace KernelScheduler { namespace OpenCL {

class Scheduler;
class Context;

class CodeLoader : public ICodeLoader
{
private:
    weak< const Context > m_context;

public:
    CodeLoader(weak< const Context > context);
    ~CodeLoader();

    virtual void load(weak< const Resource::IDescription > codeDescription,
                      Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > codeDescription,
                        Resource::Resource&                  resource) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL
