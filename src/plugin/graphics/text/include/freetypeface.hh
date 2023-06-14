/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_FREETYPEFACE_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_FREETYPEFACE_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <ft2build.h>
#include FT_FREETYPE_H
#include <motor/minitl/allocator.hh>

namespace Motor {

class FreetypeLibrary;

class FreetypeFace : public minitl::refcountable
{
public:
    FreetypeFace(const weak< FreetypeLibrary >&        freetype,
                 const minitl::allocator::block< u8 >& buffer);
    ~FreetypeFace() override;
};

}  // namespace Motor

#endif
