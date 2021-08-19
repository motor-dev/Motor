/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_COMPONENT_STORAGECONFIGURATION_SCRIPT_HH_
#define MOTOR_WORLD_COMPONENT_STORAGECONFIGURATION_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/scheduler/task/itask.hh>

namespace Motor { namespace World { namespace Component {

class motor_api(WORLD) StorageConfiguration : public minitl::refcountable
{
private:
    ref< Task::ITask > m_updateStart;

private:
    void update();

public:
    weak< Task::ITask > updateStart() const
    {
        return m_updateStart;
    }

published:
    StorageConfiguration();
    ~StorageConfiguration();
};

}}}  // namespace Motor::World::Component

/**************************************************************************************************/
#endif
