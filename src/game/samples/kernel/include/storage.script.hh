/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_SAMPLES_KERNEL_STORAGE_SCRIPT_HH_
#define BE_SAMPLES_KERNEL_STORAGE_SCRIPT_HH_
/*****************************************************************************/
#include    <world/entitystorage.script.hh>
#include    <scheduler/kernel/stream.hh>
#include    <scheduler/kernel/product.hh>

namespace BugEngine
{

class KernelStorage : public World::EntityStorage
{
private:
    scoped< BugEngine::Kernel::Stream<u32> >    m_stream1;
    scoped< BugEngine::Kernel::Stream<u32> >    m_stream2;
published:
    BugEngine::Kernel::Product<u32> const   components1;
    BugEngine::Kernel::Product<u32> const   components2;
published:
    KernelStorage();
    ~KernelStorage();
};

}

/*****************************************************************************/
#endif