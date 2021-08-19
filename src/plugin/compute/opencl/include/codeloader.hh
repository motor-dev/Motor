/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_OPENCL_CODELOADER_HH_
#define MOTOR_COMPUTE_OPENCL_CODELOADER_HH_
/**************************************************************************************************/
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

    virtual void load(weak< const Resource::Description > kernelDescription,
                      Resource::Resource&                 resource) override;
    virtual void reload(weak< const Resource::Description > oldKernelDescription,
                        weak< const Resource::Description > newKernelDescription,
                        Resource::Resource&                 resource) override;
    virtual void unload(Resource::Resource& resource) override;
};

}}}  // namespace Motor::KernelScheduler::OpenCL

/**************************************************************************************************/
#endif
