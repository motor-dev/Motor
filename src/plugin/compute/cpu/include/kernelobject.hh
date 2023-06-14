/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_COMPUTE_CPU_KERNELOBJECT_HH
#define MOTOR_PLUGIN_COMPUTE_CPU_KERNELOBJECT_HH

#include <motor/plugin.compute.cpu/stdafx.h>
#include <motor/scheduler/task/iexecutor.hh>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeObject;
class Scheduler;

class KernelObject : public Task::IExecutor
{
    friend class Scheduler;

private:
    typedef void(KernelMain)(const u32, const u32);

    class Callback;

private:
    KernelMain* m_entryPoint;

public:
    KernelObject(const weak< const CodeObject >& code, istring name);
    ~KernelObject() override;

    void run(u32 partIndex, u32 partCount) const override;
};

}}}  // namespace Motor::KernelScheduler::CPU

#endif
