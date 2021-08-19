/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_IKERNELLOADER_HH_
#define MOTOR_SCHEDULER_KERNEL_IKERNELLOADER_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor { namespace KernelScheduler {

class ICodeLoader;

class motor_api(SCHEDULER) IKernelLoader : public Resource::ILoader
{
    MOTOR_NOCOPY(IKernelLoader);

protected:
    const ref< ICodeLoader > m_codeLoader;

protected:
    IKernelLoader(ref< ICodeLoader > codeLoader);
    ~IKernelLoader();

public:
    weak< const ICodeLoader > codeLoader() const
    {
        return m_codeLoader;
    }
    weak< ICodeLoader > codeLoader()
    {
        return m_codeLoader;
    }
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
