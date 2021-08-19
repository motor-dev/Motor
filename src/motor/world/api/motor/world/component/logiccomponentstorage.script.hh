/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WORLD_COMPONENT_LOGICCOMPONENTSTORAGE_SCRIPT_HH_
#define MOTOR_WORLD_COMPONENT_LOGICCOMPONENTSTORAGE_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/world/stdafx.h>
#include <motor/world/component/icomponentstorage.script.hh>
#include <motor/world/component/storageconfiguration.script.hh>

#include <motor/introspect/simplepolicy.factory.hh>
#include <motor/scheduler/kernel/iproduct.script.hh>
#include <motor/scheduler/kernel/parameters/iparameter.script.hh>

namespace Motor { namespace World { namespace Component {

class motor_api(WORLD) LogicComponentStorage : public IComponentStorage
{
public:
    class IntrospectionHint : public Meta::AST::IntrospectionHint
    {
    protected:
        virtual bool getPropertyType(Meta::AST::DbContext& context, const istring name,
                                     Meta::Type& propertyType) const override;

    public:
        IntrospectionHint(weak< const Meta::AST::Object > owner, const Meta::CallInfo& callInfo,
                          u32 argumentThis);
        ~IntrospectionHint();
    };

published:
    motor_tag(Meta::AST::SimplePolicy< LogicComponentStorage::IntrospectionHint >())
        LogicComponentStorage(weak< StorageConfiguration > configuration,
                              raw< const Meta::Class >     componentType);

    const ref< KernelScheduler::IProduct > components;
};

}}}  // namespace Motor::World::Component

/**************************************************************************************************/
#endif
