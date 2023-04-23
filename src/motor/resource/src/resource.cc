/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

static const Handle s_nullHandle = {{nullptr}, 0};

Resource::Resource() : m_handle(s_nullHandle)
{
}

Resource::~Resource()
{
    motor_assert(m_handle.id.intId == 0,
                 "resource handle destroyed but hasn't been properly unloaded");
}

Resource::Resource(const Resource& other) = default;

Resource& Resource::operator=(const Resource& other) = default;

Resource& Resource::null()
{
    static Resource s_nullResource;
    return s_nullResource;
}

void Resource::setRefHandle(const ref< minitl::refcountable >& handle)
{
    motor_assert(m_handle.id.ptrId == nullptr,
                 "setRefHandle called but handle already has a value; use "
                 "clearRefHandle before calling setRefHandle");
    minitl::refcountable* object = handle.operator->();
    if(object)
    {
        object->addref();
        m_handle.id.ptrId = object;
    }
}

void Resource::clearRefHandle()
{
    auto* object = (minitl::refcountable*)m_handle.id.ptrId;
    if(object)
    {
        object->decref();
        m_handle.id.ptrId = nullptr;
    }
}

minitl::refcountable* Resource::getRefHandleInternal() const
{
    return (minitl::refcountable*)m_handle.id.ptrId;
}

}}  // namespace Motor::Resource
