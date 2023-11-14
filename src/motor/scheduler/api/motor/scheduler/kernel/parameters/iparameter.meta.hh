/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SCHEDULER_KERNEL_PARAMETERS_IPARAMETER_HH
#define MOTOR_SCHEDULER_KERNEL_PARAMETERS_IPARAMETER_HH

#include <motor/scheduler/stdafx.h>

namespace Motor { namespace Task {

class ITask;

}}  // namespace Motor::Task

namespace Motor { namespace KernelScheduler {

class IMemoryBuffer;
class IMemoryHost;

class motor_api(SCHEDULER) IParameter : public minitl::pointer
{
protected:
    typedef minitl::vector< minitl::tuple< raw< const Meta::Class >, raw< const Meta::Class > > >
        ParameterRegistry;

private:
    enum
    {
        BufferCount = 2
    };

    scoped< const IMemoryBuffer > m_buffers[BufferCount];

protected:
    IParameter();
    ~IParameter() override;

public:
    weak< const IMemoryBuffer > getCurrentBank() const;
    weak< const IMemoryBuffer > getBank(const weak< const IMemoryHost >& host) const;

    static istring getProductTypePropertyName();
};

class motor_api(SCHEDULER) IImage1D : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

class motor_api(SCHEDULER) IImage2D : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

class motor_api(SCHEDULER) IImage3D : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

class motor_api(SCHEDULER) ISegment : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

class motor_api(SCHEDULER) ISegments : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

class motor_api(SCHEDULER) IStream : public IParameter
{
protected:
    struct motor_api(SCHEDULER) ParameterRegistration
    {
    private:
        raw< const Meta::Class > m_key;

    private:
        static ParameterRegistry& registry();

    public:
        ParameterRegistration(raw< const Meta::Class > key, raw< const Meta::Class > parameter);
        ~ParameterRegistration();

        static raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass);
    };

public:
    static inline raw< const Meta::Class > getParameter(raw< const Meta::Class > objectClass)
    {
        return ParameterRegistration::getParameter(objectClass);
    }
};

}}  // namespace Motor::KernelScheduler

#endif
