/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Plugin {

Context::Context(const weak< Resource::ResourceManager >& manager, const ref< Folder >& folder,
                 const weak< Scheduler >& scheduler)
    : resourceManager(manager)
    , dataFolder(folder)
    , scheduler(scheduler)
{
}

}}  // namespace Motor::Plugin
