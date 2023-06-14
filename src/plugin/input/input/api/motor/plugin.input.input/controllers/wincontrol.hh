/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_WINCONTROL_HH
#define MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_WINCONTROL_HH

#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Wincontrol : public Controller
{
public:
    Wincontrol();
    ~Wincontrol() override;
};

}}  // namespace Motor::Input

#endif
