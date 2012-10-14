/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_SCHEDULER_KERNEL_ISTREAM_HH_
#define BE_SCHEDULER_KERNEL_ISTREAM_HH_
/*****************************************************************************/
#include    <scheduler/kernel/imemorybank.hh>
#include    <scheduler/task/itask.hh>

namespace BugEngine { namespace Kernel
{

class IMemoryProvider;
class IMemoryBank;

class be_api(SCHEDULER) IStream : public minitl::refcountable
{
private:
    enum BankState
    {
        Freed,
        Reserved,
        Updated
    };
public:
    struct MemoryState
    {
        weak<const IMemoryProvider> provider;
        weak<IMemoryBank>           bank;
        BankState                   state;

        static const MemoryState null;
        operator const void*() const    { return (const void*)(this - &null); }
        bool operator!() const          { return this == &null; }
    };
    static const u32 s_memoryStatesCount = 8;
private:
    MemoryState         m_states[s_memoryStatesCount];
public:
    const MemoryState& getBank(weak<const IMemoryProvider> provider) const;
};

}}

/*****************************************************************************/
#endif
