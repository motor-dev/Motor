/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <diskwatch.hh>
#include <motor/filesystem/diskfolder.script.hh>
#include <watchpoint.hh>

namespace Motor {

DiskFolder::Watch::Watch(weak< DiskFolder > folder, weak< FileSystem::WatchPoint > watchPoint)
    : Folder::Watch(folder)
    , m_watchPoint(watchPoint)
{
    m_watchPoint->addWatch(this);
}

DiskFolder::Watch::~Watch()
{
    m_watchPoint->removeWatch(this);
}

}  // namespace Motor
