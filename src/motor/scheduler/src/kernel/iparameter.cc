/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/imemoryhost.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

namespace Motor { namespace KernelScheduler {

IParameter::IParameter()
{
}

IParameter::~IParameter()
{
}

weak< const IMemoryBuffer > IParameter::getCurrentBank() const
{
    return m_buffers[0];
}

weak< const IMemoryBuffer > IParameter::getBank(weak< const IMemoryHost > host) const
{
    for(u32 i = 0; i < BufferCount; ++i)
    {
        if(m_buffers[i] && m_buffers[i]->getHost() == host) return m_buffers[i];
    }
    return weak< const IMemoryBuffer >();
}

istring IParameter::getProductTypePropertyName()
{
    static const istring s_productClassName("ProductClass");
    return s_productClassName;
}

IParameter::ParameterRegistry IImage1D::ParameterRegistration::s_registry(Arena::task());
IParameter::ParameterRegistry IImage2D::ParameterRegistration::s_registry(Arena::task());
IParameter::ParameterRegistry IImage3D::ParameterRegistration::s_registry(Arena::task());
IParameter::ParameterRegistry ISegment::ParameterRegistration::s_registry(Arena::task());
IParameter::ParameterRegistry ISegments::ParameterRegistration::s_registry(Arena::task());
IParameter::ParameterRegistry IStream::ParameterRegistration::s_registry(Arena::task());

IImage1D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

IImage2D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

IImage3D::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

ISegment::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                       raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

ISegments::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                        raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

IStream::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > key,
                                                      raw< const Meta::Class > parameter)
    : m_key(key)
{
    s_registry.push_back(minitl::make_tuple(key, parameter));
}

IImage1D::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

IImage2D::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

IImage3D::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

ISegment::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

ISegments::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

IStream::ParameterRegistration::~ParameterRegistration()
{
    for(IParameter::ParameterRegistry::iterator it = s_registry.begin(); it != s_registry.end();
        ++it)
    {
        if(it->first == m_key)
        {
            s_registry.erase(it);
            return;
        }
    }
    motor_notreached();
}

raw< const Meta::Class >
IImage1D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

raw< const Meta::Class >
IImage2D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

raw< const Meta::Class >
IImage3D::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

raw< const Meta::Class >
ISegment::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

raw< const Meta::Class >
ISegments::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

raw< const Meta::Class >
IStream::ParameterRegistration::getParameter(raw< const Meta::Class > objectClass)
{
    for(ParameterRegistry::const_iterator it = s_registry.begin(); it != s_registry.end(); ++it)
        if(it->first == objectClass) return it->second;
    return raw< const Meta::Class >();
}

}}  // namespace Motor::KernelScheduler
