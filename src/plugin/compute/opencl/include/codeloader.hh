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
    explicit CodeLoader(const weak< const Context >& context);
    ~CodeLoader() override;

    void load(const weak< const Resource::IDescription >& codeDescription,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& codeDescription,
                Resource::Resource&                         resource) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL
