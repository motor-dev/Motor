
/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/component/storageconfiguration.script.hh>

#include <motor/scheduler/task/method.hh>

namespace Motor { namespace World { namespace Component {

StorageConfiguration::StorageConfiguration()
    : m_updateStart(
        ref< Task::Task<
            Task::MethodCaller< StorageConfiguration, &StorageConfiguration::update > > >::
            create(Arena::task(), "storage:update", Colors::make(89, 89, 180),
                   Task::MethodCaller< StorageConfiguration, &StorageConfiguration::update >(this)))
{
}

StorageConfiguration::~StorageConfiguration()
{
}

void StorageConfiguration::update()
{
    // motor_info("storage update");
}

}}}  // namespace Motor::World::Component
