/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CUDA_CODELOADER_HH
#define MOTOR_PLUGIN_COMPUTE_CUDA_CODELOADER_HH

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

#endif
