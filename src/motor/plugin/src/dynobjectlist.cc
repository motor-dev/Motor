/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/plugin/dynobjectlist.hh>
#include <cstring>

namespace Motor { namespace Plugin {

#ifdef MOTOR_STATIC

DynamicObjectList* DynamicObjectList::s_dynamicObjectRoot = 0;

DynamicObjectList::Symbol::Symbol() : name(0), symbol()
{
}

DynamicObjectList::DynamicObjectList(const char* name)
    : m_next(s_dynamicObjectRoot)
    , m_name(name)
    , m_symbolCount(0)
{
    motor_info("Registering built-in dynamic object %s" | name);
    s_dynamicObjectRoot = this;
}

DynamicObjectList::~DynamicObjectList()
{
    motor_assert(s_dynamicObjectRoot == this, "Invalid order in create/destroy dynamic object");
    s_dynamicObjectRoot = m_next;
}

DynamicObjectList* DynamicObjectList::findDynamicObject(const char* name)
{
    motor_info("loading dynamic object %s (built-in)" | name);
    DynamicObjectList* current = s_dynamicObjectRoot;
    while(current)
    {
        if(strcmp(name, current->m_name) == 0)
        {
            return current;
        }
        current = current->m_next;
    }
    motor_info("unable to load dynamic object %s" | name);
    return 0;
}

bool DynamicObjectList::registerSymbolInternal(const char* name, SymbolPointer value)
{
    if(m_symbolCount < sizeof(m_symbols) / sizeof(m_symbols[0]))
    {
        m_symbols[m_symbolCount].name   = name;
        m_symbols[m_symbolCount].symbol = value;
        m_symbolCount++;
        return true;
    }
    motor_notreached();
    return false;
}

const DynamicObjectList::SymbolPointer*
DynamicObjectList::findSymbolInternal(const char* name) const
{
    for(u32 i = 0; i < m_symbolCount; ++i)
    {
        if(strcmp(m_symbols[i].name, name) == 0)
        {
            return &m_symbols[i].symbol;
        }
    }
    return 0;
}

void DynamicObjectList::showList()
{
    DynamicObjectList* object = s_dynamicObjectRoot;
    while(object)
    {
        motor_info("registered built-in plugin %s" | object->m_name);
        object = object->m_next;
    }
}

DynamicObject::Handle DynamicObject::load(const inamespace& objectName, const ipath& objectPath)
{
    motor_forceuse(objectPath);
    return (Handle)DynamicObjectList::findDynamicObject(objectName.str().name);
}

void DynamicObject::unload(Handle handle)
{
    motor_forceuse(handle);
}

void* DynamicObject::getSymbolInternal(Handle handle, const istring& name)
{
    return reinterpret_cast< DynamicObjectList* >(handle)->findSymbol< void* >(name.c_str());
}

#endif

}}  // namespace Motor::Plugin
