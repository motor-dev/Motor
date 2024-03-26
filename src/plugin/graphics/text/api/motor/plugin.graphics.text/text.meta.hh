/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_TEXT_META_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_TEXT_META_HH

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

#include <motor/plugin.graphics.text/text.meta.factory.hh>
#endif
