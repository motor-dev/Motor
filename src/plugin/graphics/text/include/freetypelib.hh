/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_FREETYPELIB_HH_
#define MOTOR_TEXT_FREETYPELIB_HH_
/**************************************************************************************************/
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
    ~FreetypeLibrary();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
