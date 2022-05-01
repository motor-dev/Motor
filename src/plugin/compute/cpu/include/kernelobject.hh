/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CPU_KERNELOBJECT_HH_
#define MOTOR_COMPUTE_CPU_KERNELOBJECT_HH_
/**************************************************************************************************/
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
    KernelObject(weak< const CodeObject > code, const istring name);
    ~KernelObject();

    virtual void run(u32 partIndex, u32 partCount) const override;
};

}}}  // namespace Motor::KernelScheduler::CPU

/**************************************************************************************************/
#endif
