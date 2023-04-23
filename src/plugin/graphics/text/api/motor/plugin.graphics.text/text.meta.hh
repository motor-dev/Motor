/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(TEXT) Text : public Resource::Description< Text >
{
public:
    Text();
    ~Text() override;
};

}  // namespace Motor
