/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_WORLD_META_HH_
#define MOTOR_WORLD_WORLD_META_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>

#include <motor/plugin/plugin.hh>
#include <motor/resource/description.hh>
#include <motor/scheduler/kernel/iproduct.meta.hh>
#include <motor/world/runtime/worldruntime.hh>

namespace Motor { namespace World {

class motor_api(WORLD) World : public Resource::Description< World >
{
private:
    minitl::array< weak< const KernelScheduler::IProduct > > m_products;

public:
    ref< WorldRuntime > createRuntime(weak< const KernelScheduler::ProducerLoader > producerLoader,
                                      const Plugin::Context&                        context) const;

published:
    World(minitl::array< weak< const KernelScheduler::IProduct > > products);
    ~World();
};

}}  // namespace Motor::World

/**************************************************************************************************/
#endif
