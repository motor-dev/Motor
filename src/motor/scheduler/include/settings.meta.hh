/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#pragma once

#include <motor/scheduler/stdafx.h>
#include <motor/settings/settings.factory.hh>

namespace Motor { namespace SchedulerSettings {

struct Scheduler : public Settings::Settings< Scheduler >
{
    enum KernelSchedulerType
    {
        Auto,
        ForceCPU,
        ForceOpenCL,
        ForceCUDA,
        ForceVulkan
    };

    Scheduler();

    i32                 ThreadCount;
    KernelSchedulerType KernelScheduler;
};

}}  // namespace Motor::SchedulerSettings
