/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_RESOURCE_HH
#define MOTOR_RESOURCE_RESOURCE_HH

#include <motor/resource/stdafx.h>

namespace Motor { namespace Resource {

struct motor_api(RESOURCE) Resource
{
    friend class IDescription;

private:
    scoped< minitl::pointer > m_handle;
    u32                       m_owner;

private:
    Resource();
    Resource(Resource && other) = default;

public:
    ~Resource();
    Resource& operator=(const Resource& other) = delete;
    Resource& operator=(Resource&& other)      = default;

    void setHandle(scoped< minitl::pointer > && handle);
    void clearHandle();
    template < typename T >
    weak< T > getHandle() const
    {
        return motor_checked_cast< T >(weak< minitl::pointer >(m_handle));
    }
    template < typename T >
    scoped< T > stealHandle()
    {
        return motor_checked_cast< T >(minitl::move(m_handle));
    }

    static Resource& null();

    operator const void*() const  // NOLINT(google-explicit-constructor)
    {
        return (const void*)(this - &null());
    }
    bool operator!() const
    {
        return !this->operator const void*();
    }
};

}}  // namespace Motor::Resource

#endif
