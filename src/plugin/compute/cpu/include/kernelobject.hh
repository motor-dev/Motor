/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_COMPUTE_CPU_KERNELOBJECT_HH_
#define MOTOR_COMPUTE_CPU_KERNELOBJECT_HH_
/**************************************************************************************************/
#include <motor/plugin.compute.cpu/stdafx.h>

namespace Motor { namespace KernelScheduler { namespace CPU {

class CodeObject;
class Scheduler;

class KernelObject : public minitl::refcountable
{
    friend class Scheduler;

private:
    typedef void(KernelMain)(const u32, const u32);

private:
    KernelMain* m_entryPoint;

public:
    KernelObject(weak< const CodeObject > code, const istring name);
    ~KernelObject();

    void run(const u32 index, const u32 total);
};

}}}  // namespace Motor::KernelScheduler::CPU

/**************************************************************************************************/
#endif
