/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_GAMEPAD_HH
#define MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_GAMEPAD_HH

#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Gamepad : public Controller
{
public:
    Gamepad();
    ~Gamepad() override;
};

}}  // namespace Motor::Input

#endif
