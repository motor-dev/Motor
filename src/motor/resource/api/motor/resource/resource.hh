/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/resource/stdafx.h>
#include <motor/resource/handle.meta.hh>

namespace Motor { namespace Resource {

struct motor_api(RESOURCE) Resource
{
    friend class IDescription;

private:
    Handle m_handle;

private:
    Resource();
    Resource(const Resource& other);
    Resource& operator=(const Resource& other);

    minitl::refcountable* getRefHandleInternal() const;

public:
    ~Resource();

    void setRefHandle(const ref< minitl::refcountable >& handle);
    void clearRefHandle();
    template < typename T >
    weak< T > getRefHandle() const
    {
        return motor_checked_cast< T >(getRefHandleInternal());
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
