/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_SCHEDULER_KERNEL_PARAMETER_IPARAMETER_SCRIPT_HH_
#define BE_SCHEDULER_KERNEL_PARAMETER_IPARAMETER_SCRIPT_HH_
/**************************************************************************************************/
#include    <scheduler/stdafx.h>

namespace BugEngine { namespace Kernel
{

class IMemoryBuffer;
class IMemoryHost;

class IParameter : public minitl::refcountable
{
private:
    enum
    {
        BufferCount = 2
    };
    ref<const IMemoryBuffer>  m_buffers[BufferCount];
protected:
    IParameter();
    ~IParameter();

public:
    weak<const IMemoryBuffer> getCurrentBank() const;
    weak<const IMemoryBuffer> getBank(weak<const IMemoryHost> host) const;
    void transfer(weak<const IMemoryHost> to);
};

}}

/**************************************************************************************************/
#endif
