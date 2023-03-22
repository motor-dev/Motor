/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <freetypelib.hh>

namespace Motor {

FreetypeLibrary::FreetypeLibrary()
{
    FT_Error error = FT_Init_FreeType(&library);
    motor_forceuse(error);
    motor_assert_format(!error, "Freetype error {0}", error);
}

FreetypeLibrary::~FreetypeLibrary()
{
    FT_Done_FreeType(library);
}

}  // namespace Motor
