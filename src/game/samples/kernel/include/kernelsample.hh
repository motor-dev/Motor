/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_SAMPLES_KERNEL_KERNELSAMPLE_HH_
#define BE_SAMPLES_KERNEL_KERNELSAMPLE_HH_
/*****************************************************************************/
#include    <system/file/folder.script.hh>
#include    <bugengine/application.hh>
#include    <system/resource/resourcemanager.hh>
#include    <system/scheduler/kernel/kernel.script.hh>
#include    <system/plugin.hh>

namespace BugEngine { namespace Samples
{

class KernelSample : public Application
{
private:
    scoped<Kernel::Kernel> m_kernelSample;
public:
    KernelSample(const PluginContext& context);
    ~KernelSample();
public:
    void* operator new(size_t size, void* where)     { return ::operator new(size, where); }
    void  operator delete(void* memory, void* where) { ::operator delete(memory, where); }
    void  operator delete(void* memory)              { be_notreached(); ::operator delete(memory); }
};

}}

/*****************************************************************************/
#endif

