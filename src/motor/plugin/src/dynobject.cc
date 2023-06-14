/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/plugin/dynobject.hh>

namespace Motor { namespace Plugin {

DynamicObject::DynamicObject(const inamespace& objectName, const ipath& objectPath)
    : m_handle(load(objectName, objectPath))
{
}

DynamicObject::~DynamicObject()
{
    if(m_handle)
    {
        unload(m_handle);
    }
}

}}  // namespace Motor::Plugin


