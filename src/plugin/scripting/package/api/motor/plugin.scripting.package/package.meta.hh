/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGE_META_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_PACKAGE_META_HH

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/meta/tags/editor.meta.hh>
#include <motor/script.hh>

namespace Motor {

class PackageLoader;

class motor_api(PACKAGE) Package : public Script< Package >
{
    friend class PackageLoader;

public:
    explicit Package(const weak< const File >& file);
    ~Package() override;
};

}  // namespace Motor

#include <motor/plugin.scripting.package/package.meta.factory.hh>
#endif
