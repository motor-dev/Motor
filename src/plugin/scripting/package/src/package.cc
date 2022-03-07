/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/plugin.scripting.package/package.meta.hh>

namespace Motor {

Package::Package(weak< const File > file) : Script<Package>(file)
{
}

Package::~Package()
{
}

}  // namespace Motor
