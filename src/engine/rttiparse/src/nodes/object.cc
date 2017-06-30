/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#include    <rttiparse/stdafx.h>
#include    <rttiparse/object.hh>
#include    <nodes/reference.hh>
#include    <rtti/value.hh>
#include    <rtti/classinfo.script.hh>


namespace BugEngine { namespace RTTI { namespace Parser
{

Object::Object(const ParseLocation& location, ref<Reference> className,
               const minitl::vector<Parameter>& parameters)
    :   Node(location)
    ,   m_className(className)
    ,   m_parameters(parameters)

{
}

Object::~Object()
{
}

bool Object::resolve(DbContext& context)
{
    bool result = m_className->resolve(context);
    for (minitl::vector<Parameter>::const_iterator it = m_parameters.begin();
         it != m_parameters.end();
         ++it)
    {
        result &= it->value->resolve(context);
    }
    return result;
}

bool Object::isCompatible(const Type &expectedType) const
{
    be_forceuse(expectedType);
    be_unimplemented();
    return true;
}

void Object::doEval(const Type &expectedType, Value &result) const
{
    be_forceuse(expectedType);
    be_forceuse(result);
    be_unimplemented();
}

Type Object::getType() const
{
    return be_typeid<void>::type();
}

}}}
