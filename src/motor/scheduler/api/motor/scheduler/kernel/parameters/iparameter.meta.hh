/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETER_IPARAMETER_META_HH_
#define MOTOR_SCHEDULER_KERNEL_PARAMETER_IPARAMETER_META_HH_
/**************************************************************************************************/
#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Task {

class ITask;

}}  // namespace Motor::Task

namespace Motor { namespace KernelScheduler {

class IMemoryBuffer;
class IMemoryHost;
class IProduct;

class motor_api(SCHEDULER) IParameter : public minitl::refcountable
{
private:
    enum
    {
        BufferCount = 2
    };

    ref< const IMemoryBuffer > m_buffers[BufferCount];

private:
    static minitl::vector< raw< const Meta::Class > >& parameterClasses();

protected:
    IParameter();
    ~IParameter();

public:
    weak< const IMemoryBuffer > getCurrentBank() const;
    weak< const IMemoryBuffer > getBank(weak< const IMemoryHost > host) const;

    static raw< const Meta::Class > getParameterClass(const istring parameterTypeName);

    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_class;

    public:
        ParameterRegistration(raw< const Meta::Class > klass);
        ~ParameterRegistration();
    };
    friend struct ParameterRegistration;
};

}}  // namespace Motor::KernelScheduler

/**************************************************************************************************/
#endif
