/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_FONTLIST_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_FONTLIST_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/minitl/pointer.hh>

namespace Motor {

class FontList : public minitl::pointer
{
public:
    FontList();
    ~FontList() override;
};

}  // namespace Motor

#endif
