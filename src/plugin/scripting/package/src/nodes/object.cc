/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <package/stdafx.h>
#include    <package/nodes/object.hh>
#include    <package/nodes/package.hh>
#include    <package/nodes/reference.hh>
#include    <package/nodes/parameter.hh>

namespace BugEngine { namespace PackageBuilder { namespace Nodes
{

Object::Object(weak<Package> owner)
    :   m_owner(owner)
    ,   m_name("")
    ,   m_method(0)
    ,   m_parameters(packageBuilderArena())
    ,   m_overloads(packageBuilderArena())
{
}

Object::~Object()
{
}

void Object::setName(istring name)
{
    if (m_owner->findByName(name))
    {
        // error
        be_unimplemented();
    }
    m_name = name;
}

void Object::setMethod(ref<Reference> reference)
{
    m_methodReference = reference;
    BugEngine::Value v(BugEngine::Value::ByRef(m_methodReference->getValue()));
    if (v)
    {
        static const istring callName("call");
        BugEngine::Value call = v[callName];
        if (call && be_typeid<const RTTI::MethodInfo* const>::type() <= call.type())
        {
            m_method = call.as<const RTTI::MethodInfo*>();
            m_overloads.clear();
            for (raw<const RTTI::MethodInfo::OverloadInfo> overload = m_method->overloads; overload; overload = overload->next)
            {
                m_overloads.push_back(OverloadMatch(overload));
                OverloadMatch& match = m_overloads.back();
                for(minitl::vector< ref<Parameter> >::const_iterator it = m_parameters.begin(); it != m_parameters.end(); ++it)
                {
                    match.addParameter(*it);
                }
            }
            minitl::sort(m_overloads.begin(), m_overloads.end(), minitl::less<OverloadMatch>());
        }
        else if (call)
        {
            // error
            be_unimplemented();
        }
        else
        {
            // error
            be_unimplemented();
        }
    }
}

void Object::addParameter(ref<Parameter> param)
{
    m_parameters.push_back(param);
    for (minitl::vector< OverloadMatch >::iterator it = m_overloads.begin(); it != m_overloads.end(); ++it)
    {
        it->addParameter(param);
    }
    minitl::sort(m_overloads.begin(), m_overloads.end(), minitl::less<OverloadMatch>());
}

TypeInfo Object::getType() const
{
    if (m_overloads.empty())
    {
        be_notreached();
        return be_typeid<void>::type();
    }
    else
    {
        return m_overloads[0].m_overload->returnType;
    }
}

BugEngine::Value Object::create() const
{
    return m_overloads.empty() ? BugEngine::Value() : m_overloads[0].create();
}

}}}