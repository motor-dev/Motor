/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_RESOURCE_HH_
#define MOTOR_RESOURCE_RESOURCE_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/resource/handle.script.hh>

namespace Motor { namespace Resource {

struct motor_api(RESOURCE) Resource
{
    friend class Description;

private:
    Handle m_handle;

private:
    Resource();
    Resource(const Resource& other);
    Resource& operator=(const Resource& other);

    minitl::refcountable* getRefHandleInternal() const;

public:
    ~Resource();

    void setRefHandle(ref< minitl::refcountable > handle);
    void clearRefHandle();
    template < typename T >
    weak< T > getRefHandle() const
    {
        return motor_checked_cast< T >(getRefHandleInternal());
    }

    static Resource& null();

    operator const void*() const
    {
        return (const void*)(this - &null());
    }
    bool operator!() const
    {
        return !this->operator const void*();
    }
};

}}  // namespace Motor::Resource

/**************************************************************************************************/
#endif
