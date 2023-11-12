/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

Resource::Resource() : m_handle(), m_owner(0)
{
}

Resource::~Resource()
{
    motor_assert(m_handle == nullptr,
                 "resource handle destroyed but hasn't been properly unloaded");
}

Resource& Resource::null()
{
    static Resource s_nullResource;
    return s_nullResource;
}

void Resource::setHandle(scoped< minitl::pointer >&& handle)
{
    motor_assert(m_handle == nullptr, "setRefHandle called but handle already has a value; use "
                                      "clearRefHandle before calling setRefHandle");
    m_handle = minitl::move(handle);
}

void Resource::clearHandle()
{
    m_handle = scoped< minitl::pointer >();
}

}}  // namespace Motor::Resource
