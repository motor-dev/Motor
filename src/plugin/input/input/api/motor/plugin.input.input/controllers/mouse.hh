/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_MOUSE_HH
#define MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_MOUSE_HH

#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Mouse : public Controller
{
public:
    Mouse();
    ~Mouse() override;
};

}}  // namespace Motor::Input

#endif
