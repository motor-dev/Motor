/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_CONTROLLERS_CONTROLLER_HH_
#define MOTOR_INPUT_CONTROLLERS_CONTROLLER_HH_
/**************************************************************************************************/
#include <motor/plugin.input.input/stdafx.h>

namespace Motor { namespace Input {

class motor_api(INPUT) Controller : public minitl::refcountable
{
    MOTOR_NOCOPY(Controller);

protected:
    Controller();
    ~Controller();
};

}}  // namespace Motor::Input

/**************************************************************************************************/
#endif
