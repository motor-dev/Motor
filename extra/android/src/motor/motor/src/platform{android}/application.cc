/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <motor/core/environment.hh>
#include <motor/filesystem/zipfolder.meta.hh>

extern const char* s_packagePath;

namespace Motor {

ref< Folder > Application::createDataFolder(const ipath& dataSubDirectory)
{
    return ref< ZipFolder >::create(Arena::game(), ipath(s_packagePath),
                                    Environment::getEnvironment().getDataDirectory()
                                        + dataSubDirectory);
}

}  // namespace Motor
