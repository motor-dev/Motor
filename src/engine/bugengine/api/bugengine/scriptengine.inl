/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_BUGENGINE_SCRIPTENGINE_INL_
#define BE_BUGENGINE_SCRIPTENGINE_INL_
/*****************************************************************************/
#include    <bugengine/stdafx.h>
#include    <bugengine/scriptengine.hh>
#include    <system/resource/resourcemanager.hh>

namespace BugEngine
{

template< typename T >
ScriptEngine<T>::ScriptEngine(Allocator& arena, weak<ResourceManager> manager)
    :   IResourceLoader()
    ,   m_scriptArena(arena)
    ,   m_manager(manager)
{
    m_manager->attach<T>(this);
}

template< typename T >
ScriptEngine<T>::~ScriptEngine()
{
    m_manager->detach<T>(this);
}

template< typename T >
ResourceHandle ScriptEngine<T>::load(weak<const Resource> resource)
{
    m_manager->addTicket(this, resource, be_checked_cast<const Script>(resource)->m_file);
    return ResourceHandle();
}

template< typename T >
void ScriptEngine<T>::unload(const ResourceHandle& handle)
{
}

template< typename T >
void ScriptEngine<T>::onTicketLoaded(weak<const Resource> resource, const Allocator::Block<u8>& buffer)
{
    runBuffer(be_checked_cast<const T>(resource), buffer);
}

}

/*****************************************************************************/
#endif