/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/filesystem/folder.script.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor { namespace Plugin {

Context::Context(weak< Resource::ResourceManager > manager, ref< Folder > folder,
                 weak< Scheduler > scheduler)
    : resourceManager(manager)
    , dataFolder(folder)
    , scheduler(scheduler)
{
}

}}  // namespace Motor::Plugin
