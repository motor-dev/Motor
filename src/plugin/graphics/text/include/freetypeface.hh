/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_FREETYPEFACE_HH_
#define MOTOR_TEXT_FREETYPEFACE_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <ft2build.h>
#include FT_FREETYPE_H
#include <motor/minitl/allocator.hh>

namespace Motor {

class FreetypeLibrary;

class FreetypeFace : public minitl::refcountable
{
public:
    FreetypeFace(weak< FreetypeLibrary > freetype, const minitl::Allocator::Block< u8 >& buffer);
    ~FreetypeFace();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
