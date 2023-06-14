/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_IKERNELLOADER_HH
#define MOTOR_SCHEDULER_KERNEL_IKERNELLOADER_HH

#include <motor/scheduler/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/scheduler/kernel/icodeloader.hh>

namespace Motor { namespace KernelScheduler {

class ICodeLoader;

class motor_api(SCHEDULER) IKernelLoader : public Resource::ILoader
{
protected:
    const ref< ICodeLoader > m_codeLoader;

protected:
    explicit IKernelLoader(const ref< ICodeLoader >& codeLoader);
    ~IKernelLoader() override;

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

#endif
