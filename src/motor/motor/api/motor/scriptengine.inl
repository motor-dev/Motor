/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_SCRIPTENGINE_INL_
#define MOTOR_MOTOR_SCRIPTENGINE_INL_
/**************************************************************************************************/
#include <motor/stdafx.h>
#include <motor/resource/resourcemanager.hh>
#include <motor/scriptengine.hh>

namespace Motor {

template < typename T >
ScriptEngine< T >::ScriptEngine(minitl::Allocator& arena, weak< Resource::ResourceManager > manager)
    : ILoader()
    , m_scriptArena(arena)
    , m_manager(manager)
{
    m_manager->attach< T >(this);
}

template < typename T >
ScriptEngine< T >::~ScriptEngine()
{
    m_manager->detach< T >(this);
}

template < typename T >
void ScriptEngine< T >::load(weak< const Resource::Description > script,
                             Resource::Resource& /*resource*/)
{
    motor_assert(motor_checked_cast< const Script >(script)->m_file,
                 "can't open script: file not found");
    m_manager->addTicket(this, script, motor_checked_cast< const Script >(script)->m_file,
                         ILoader::FileText, ILoader::LoadFirstTime);
}

template < typename T >
void ScriptEngine< T >::reload(weak< const Resource::Description > /*oldScript*/,
                               weak< const Resource::Description > newScript,
                               Resource::Resource& /*resource*/)
{
    motor_assert(motor_checked_cast< const Script >(newScript)->m_file,
                 "can't open script: file not found");
    m_manager->addTicket(this, newScript, motor_checked_cast< const Script >(newScript)->m_file,
                         ILoader::FileText, ILoader::LoadReload);
}

template < typename T >
void ScriptEngine< T >::onTicketLoaded(weak< const Resource::Description >   script,
                                       Resource::Resource&                   resource,
                                       const minitl::Allocator::Block< u8 >& buffer,
                                       ILoader::LoadType                     type)
{
    if(type == ILoader::LoadReload)
    {
        reloadBuffer(motor_checked_cast< const T >(script), resource, buffer);
    }
    else
    {
        runBuffer(motor_checked_cast< const T >(script), resource, buffer);
    }
}

}  // namespace Motor

/**************************************************************************************************/
#endif
