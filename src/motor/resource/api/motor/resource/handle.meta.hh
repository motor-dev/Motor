/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_HANDLE_HH_
#define MOTOR_RESOURCE_HANDLE_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>

namespace Motor { namespace Resource {

class ILoader;

struct motor_api(RESOURCE) Handle
{
    union Id
    {
        void* ptrId;
        u32   intId;
    };
    Id  id;
    u32 owner;
};

}}  // namespace Motor::Resource

/**************************************************************************************************/
#endif
