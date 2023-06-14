/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_FREETYPELIB_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_FREETYPELIB_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <ft2build.h>
#include FT_FREETYPE_H

namespace Motor {

class FreetypeLibrary : public minitl::pointer
{
public:
    FT_Library library;

public:
    FreetypeLibrary();
    ~FreetypeLibrary() override;
};

}  // namespace Motor

#endif
