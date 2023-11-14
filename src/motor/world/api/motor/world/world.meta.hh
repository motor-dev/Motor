/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_WORLD_META_HH
#define MOTOR_WORLD_WORLD_META_HH

#include <motor/world/stdafx.h>
#include <motor/world/componentregistry.meta.hh>

#include <motor/plugin/plugin.hh>
#include <motor/resource/description.hh>
#include <motor/scheduler/kernel/producer.meta.hh>

namespace Motor { namespace KernelScheduler {

class IProduct;
class ProducerLoader;

}}  // namespace Motor::KernelScheduler

namespace Motor { namespace World {

class WorldRuntime;

class motor_api(WORLD) World : public Resource::Description< World >
{
private:
    ref< ComponentRegistry >                                  m_registry;
    minitl::vector< weak< const KernelScheduler::IProduct > > m_products;

public:
    [[motor::meta(noexport)]] scoped< WorldRuntime > createRuntime(
        const weak< const KernelScheduler::ProducerLoader >& producerLoader,
        const Plugin::Context&                               context) const;

public:
    World(const ref< ComponentRegistry >&                           registry,
          minitl::vector< weak< const KernelScheduler::IProduct > > products);
    ~World() override;
};

}}  // namespace Motor::World

#endif
