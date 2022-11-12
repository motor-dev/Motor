/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor { namespace KernelScheduler {

class motor_api(SCHEDULER) ICodeLoader : public Resource::ILoader
{
    MOTOR_NOCOPY(ICodeLoader);

protected:
    ICodeLoader();
    ~ICodeLoader();
};

}}  // namespace Motor::KernelScheduler
