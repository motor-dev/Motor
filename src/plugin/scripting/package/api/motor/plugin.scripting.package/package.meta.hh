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
    Package(weak< const File > file);
    ~Package();
};

}  // namespace Motor
