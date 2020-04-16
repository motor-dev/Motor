/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#include    <cuda/stdafx.h>
#include    <memoryhost.hh>

namespace BugEngine { namespace KernelScheduler { namespace Cuda
{

MemoryHost::MemoryHost()
    :   IMemoryHost("Cuda")
{
}

MemoryHost::~MemoryHost()
{
}

}}}