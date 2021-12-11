/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_DESCRIPTION_HH_
#define MOTOR_RESOURCE_DESCRIPTION_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>

#include <motor/resource/idescription.meta.hh>

namespace Motor { namespace Resource {

template < typename T >
class Description : public IDescription
{
protected:
    Description() : IDescription()
    {
    }
    ~Description()
    {
    }
};

}}  // namespace Motor::Resource

#include <motor/resource/description.factory.hh>

/**************************************************************************************************/
#endif
