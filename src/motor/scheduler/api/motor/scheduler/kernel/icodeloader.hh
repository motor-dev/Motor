/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_ICODELOADER_HH
#define MOTOR_SCHEDULER_KERNEL_ICODELOADER_HH

#include <motor/scheduler/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) ICodeLoader : public Resource::ILoader
{
protected:
    ICodeLoader();
    ~ICodeLoader() override;
};

}}  // namespace Motor::KernelScheduler

#endif
