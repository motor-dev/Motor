/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_CONTROLLERS_KEYBOARD_HH_
#define MOTOR_INPUT_CONTROLLERS_KEYBOARD_HH_
/**************************************************************************************************/
#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Keyboard : public Controller
{
    MOTOR_NOCOPY(Keyboard);

public:
    Keyboard();
    ~Keyboard();
};

}}  // namespace Motor::Input

/**************************************************************************************************/
#endif
