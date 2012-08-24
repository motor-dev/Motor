/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_SAMPLES_KERNEL_KERNELTASK_SCRIPT_HH_
#define BE_SAMPLES_KERNEL_KERNELTASK_SCRIPT_HH_
/*****************************************************************************/
#include    <scheduler/kernel/kernel.script.hh>
#include    <scheduler/task/itask.hh>
#include    <resource/resource.script.hh>
#include    <scheduler/kernel/product.hh>

namespace BugEngine
{

class KernelSampleTask : public Kernel::Kernel
{
private:
    scoped< BugEngine::Task::ITask > const  m_kernelTask;
    BugEngine::Kernel::Product< u32 > const m_input1;
    BugEngine::Kernel::Product< u32 > const m_input2;
    Task::ITask::CallbackConnection const   m_chainInput1;
    Task::ITask::CallbackConnection const   m_chainInput2;
published:
    BugEngine::Kernel::Product< u32 > const output;
published:
    KernelSampleTask(BugEngine::Kernel::Product< u32 > const in1, BugEngine::Kernel::Product< u32 > const out1);
    ~KernelSampleTask();
};

}

/*****************************************************************************/
#endif
