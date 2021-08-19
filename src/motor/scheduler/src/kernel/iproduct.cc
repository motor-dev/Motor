/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>
#include <motor/scheduler/kernel/iproduct.script.hh>

namespace Motor {

raw< Meta::Class > motor_motor_Namespace_Motor_KernelScheduler();

namespace KernelScheduler {

IProduct::~IProduct()
{
}

void IProduct::addOutputHost(weak< IMemoryHost > host)
{
    for(minitl::vector< HostInformation >::iterator it = m_productOutput.begin();
        it != m_productOutput.end(); ++it)
    {
        if(it->first == host)
        {
            ++it->second;
            return;
        }
    }
    m_productOutput.push_back(HostInformation(host, 1));
}

void IProduct::removeOutputHost(weak< IMemoryHost > host)
{
    for(minitl::vector< HostInformation >::iterator it = m_productOutput.begin();
        it != m_productOutput.end(); ++it)
    {
        if(it->first == host)
        {
            if(--it->second == 0) m_productOutput.erase(it);
            return;
        }
    }
    motor_notreached();
}

raw< Meta::Class > IProduct::getNamespace()
{
    return motor_motor_Namespace_Motor_KernelScheduler();
}

}  // namespace KernelScheduler
}  // namespace Motor
