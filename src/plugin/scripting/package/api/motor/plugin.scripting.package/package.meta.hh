/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PACKAGE_PACKAGE_META_HH_
#define MOTOR_PACKAGE_PACKAGE_META_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.meta.hh>

namespace Motor {

class PackageLoader;

class motor_api(PACKAGE) Package : public Script
{
    friend class PackageLoader;
published:
    Package(weak< const File > file);
    ~Package();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
