/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_CONTROLLERS_MOUSE_HH_
#define MOTOR_INPUT_CONTROLLERS_MOUSE_HH_
/**************************************************************************************************/
#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Mouse : public Controller
{
    MOTOR_NOCOPY(Mouse);

public:
    Mouse();
    ~Mouse();
};

}}  // namespace Motor::Input

/**************************************************************************************************/
#endif
