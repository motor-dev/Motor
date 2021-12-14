/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_WORLDLOADER_HH_
#define MOTOR_WORLD_WORLDLOADER_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/resource/loader.hh>

#include <motor/plugin/plugin.hh>
#include <motor/scheduler/kernel/producerloader.hh>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace World {

class motor_api(WORLD) WorldLoader : public Resource::ILoader
{
private:
    class WorldResource;

private:
    weak< Task::ITask >                           m_loopTask;
    minitl::vector< ref< WorldResource > >        m_worlds;
    weak< const KernelScheduler::ProducerLoader > m_producerLoader;
    Plugin::Context                               m_pluginContext;
    u32                                           m_worldCount;

private:
    virtual void load(weak< const Resource::IDescription > world, Resource::Resource & resource)
        override;
    virtual void unload(weak< const Resource::IDescription > world, Resource::Resource & resource)
        override;

public:
    WorldLoader(weak< Task::ITask >                     loopTask,
                weak< KernelScheduler::ProducerLoader > producerLoader,
                const Plugin::Context&                  pluginContext);
    ~WorldLoader();

    void disconnectWorlds();
    u32  worldCount() const
    {
        return m_worldCount;
    }
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
