/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_CONTROLLERS_GAMEPAD_HH_
#define MOTOR_INPUT_CONTROLLERS_GAMEPAD_HH_
/**************************************************************************************************/
#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Gamepad : public Controller
{
    MOTOR_NOCOPY(Gamepad);

public:
    Gamepad();
    ~Gamepad();
};

}}  // namespace Motor::Input

/**************************************************************************************************/
#endif
