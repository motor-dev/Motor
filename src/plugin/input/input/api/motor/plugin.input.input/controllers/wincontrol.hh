/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
