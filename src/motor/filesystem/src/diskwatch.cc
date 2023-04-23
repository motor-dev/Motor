/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/diskfolder.meta.hh>
#include <diskwatch.hh>
#include <watchpoint.hh>

namespace Motor {

DiskFolder::Watch::Watch(const weak< DiskFolder >&             folder,
                         const weak< FileSystem::WatchPoint >& watchPoint)
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
