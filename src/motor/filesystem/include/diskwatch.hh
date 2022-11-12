/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/diskfolder.meta.hh>

namespace Motor {

namespace FileSystem {
class WatchPoint;
}

class DiskFolder::Watch : public Folder::Watch
{
private:
    weak< FileSystem::WatchPoint > m_watchPoint;

public:
    Watch(weak< DiskFolder > folder, weak< FileSystem::WatchPoint > watchPoint);
    ~Watch();
};

}  // namespace Motor
