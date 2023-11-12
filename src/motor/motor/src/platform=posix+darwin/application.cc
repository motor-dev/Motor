/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/environment.hh>
#include <motor/filesystem/diskfolder.meta.hh>

namespace Motor {

ref< Folder > Application::createDataFolder(const ipath& dataSubDirectory)
{
    ipath fullPath = Environment::getEnvironment().getDataDirectory() + dataSubDirectory;
    return ref< DiskFolder >::create(Arena::game(), fullPath);
}

}  // namespace Motor
