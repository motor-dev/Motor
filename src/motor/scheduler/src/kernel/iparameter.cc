/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/imemoryhost.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

namespace Motor { namespace KernelScheduler {

IParameter::IParameter() = default;

IParameter::~IParameter() = default;

weak< const IMemoryBuffer > IParameter::getCurrentBank() const
{
    return m_buffers[0];
}

weak< const IMemoryBuffer > IParameter::getBank(const weak< const IMemoryHost >& host) const
{
    for(const auto& m_buffer: m_buffers)
    {
        if(m_buffer && m_buffer->getHost() == host) return m_buffer;
    }
    return {};
}

istring IParameter::getProductTypePropertyName()
{
    static const istring s_productClassName("ProductClass");
    return s_productClassName;
}

IParameter::ParameterRegistry& IImage1D::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IParameter::ParameterRegistry& IImage2D::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IParameter::ParameterRegistry& IImage3D::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IParameter::ParameterRegistry& ISegment::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IParameter::ParameterRegistry& ISegments::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IParameter::ParameterRegistry& IStream::ParameterRegistration::registry()
{
    static IParameter::ParameterRegistry s_registry(Arena::task());
    return s_registry;
}

IImage1D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

IImage2D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

IImage3D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

ISegment::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

ISegments::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                        raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

IStream::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                      raw< const Meta::Class > parameter)
    : m_key(key)
{
    registry().push_back(minitl::make_tuple(key, parameter));
}

IImage1D::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

IImage2D::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

IImage3D::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

ISegment::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

ISegments::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

IStream::ParameterRegistration::~ParameterRegistration()
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::iterator it = reg.begin(); it != reg.end(); ++it)
    {
        if(it->first == m_key)
        {
            reg.erase(it);
            return;
        }
    }
    motor_notreached();
}

raw< const Meta::Class >
IImage1D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

raw< const Meta::Class >
IImage2D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

raw< const Meta::Class >
IImage3D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

raw< const Meta::Class >
ISegment::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

raw< const Meta::Class >
ISegments::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

raw< const Meta::Class >
IStream::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    ParameterRegistry& reg = registry();
    for(ParameterRegistry::const_iterator it = reg.begin(); it != reg.end(); ++it)
        if(it->first == objectClass) return it->second;
    return {};
}

}}  // namespace Motor::KernelScheduler
