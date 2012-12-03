/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_KERNEL_CPU_CPUMEMORYBANK_HH_
#define BE_KERNEL_CPU_CPUMEMORYBANK_HH_
/*****************************************************************************/
#include    <scheduler/kernel/imemorybank.hh>

namespace BugEngine
{

class CPUMemoryProvider;

class CPUMemoryBank : public Kernel::IMemoryBank
{
public:
    CPUMemoryBank(weak<const CPUMemoryProvider> provider);
    ~CPUMemoryBank();
};

}

/*****************************************************************************/
#endif