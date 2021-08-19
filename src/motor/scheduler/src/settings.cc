/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */

#include <settings.script.hh>

namespace Motor { namespace SchedulerSettings {

Scheduler::Scheduler() : ThreadCount(0), KernelScheduler(Auto)
{
}

}}  // namespace Motor::SchedulerSettings
