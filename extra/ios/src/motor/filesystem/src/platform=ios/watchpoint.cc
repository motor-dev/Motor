/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <watchpoint.hh>

namespace Motor { namespace FileSystem {

ref< Folder::Watch > WatchPoint::addWatch(weak< DiskFolder > /*folder*/,
                                          const Motor::ipath& /*path*/)
{
    return ref< Folder::Watch >();
}

}}  // namespace Motor::FileSystem
