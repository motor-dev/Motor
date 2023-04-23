/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class LuaScript : public Script< LuaScript >
{
    friend class PackageLoader;
    published
        : explicit LuaScript(motor_tag(EditHint::Extension(".lua"))
                                 const weak< const File >& script);
    ~LuaScript() override;
};

}  // namespace Motor
