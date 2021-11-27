/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/scheduler/stdafx.h>
#include <motor/scheduler/kernel/imemorybuffer.hh>
#include <motor/scheduler/kernel/imemoryhost.hh>
#include <motor/scheduler/kernel/parameters/iparameter.meta.hh>

namespace Motor { namespace KernelScheduler {

IParameter::ParameterRegistration::ParameterRegistration(raw< const Meta::Class > klass)
    : m_class(klass)
{
    IParameter::parameterClasses().push_back(klass);
}

IParameter::ParameterRegistration::~ParameterRegistration()
{
    minitl::vector< raw< const Meta::Class > >& classes = IParameter::parameterClasses();
    for(minitl::vector< raw< const Meta::Class > >::iterator it = classes.begin();
        it != classes.end(); ++it)
    {
        if(*it == m_class)
        {
            classes.erase(it);
            break;
        }
    }
}

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

raw< const Meta::Class > IParameter::getParameterClass(istring parameterClassName)
{
    minitl::vector< raw< const Meta::Class > > classes = IParameter::parameterClasses();
    for(minitl::vector< raw< const Meta::Class > >::iterator it = classes.begin();
        it != classes.end(); ++it)
    {
        if((*it)->name == parameterClassName) return *it;
    }
    return raw< const Meta::Class >();
}

minitl::vector< raw< const Meta::Class > >& IParameter::parameterClasses()
{
    static minitl::vector< raw< const Meta::Class > > s_classes(Arena::meta());
    return s_classes;
}

}}  // namespace Motor::KernelScheduler
