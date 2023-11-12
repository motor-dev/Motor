/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_WORLDLOADER_HH
#define MOTOR_WORLD_WORLDLOADER_HH

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
    minitl::vector< weak< WorldResource > >       m_worlds;
    weak< const KernelScheduler::ProducerLoader > m_producerLoader;
    Plugin::Context                               m_pluginContext;
    u32                                           m_worldCount;

private:
    void load(const weak< const Resource::IDescription >& worldDescription,
              Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& worldDescription,
                Resource::Resource&                         resource) override;

public:
    WorldLoader(const weak< Task::ITask >&                     loopTask,
                const weak< KernelScheduler::ProducerLoader >& producerLoader,
                Plugin::Context                                pluginContext);
    ~WorldLoader() override;

    void disconnectWorlds();
    u32  worldCount() const
    {
        return m_worldCount;
    }
};

}}  // namespace Motor::World

#endif
