/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_DESCRIPTION_HH
#define MOTOR_RESOURCE_DESCRIPTION_HH

#include <motor/resource/stdafx.h>

#include <motor/resource/idescription.meta.hh>

namespace Motor { namespace Resource {

template < typename T >
class Description : public IDescription
{
protected:
    Description()           = default;
    ~Description() override = default;
};

}}  // namespace Motor::Resource

#endif
