/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class PackageLoader;

class motor_api(PACKAGE) Package : public Script< Package >
{
    friend class PackageLoader;
published:
    explicit Package(const weak< const File >& file);
    ~Package() override;
};

}  // namespace Motor
