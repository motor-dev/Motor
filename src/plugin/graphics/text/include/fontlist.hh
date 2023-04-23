/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
