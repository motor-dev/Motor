#include <motor/world/component/logiccomponentstorage.script.hh>

int main()
{
    using namespace Motor;
    using namespace Motor::World::Component;

    ref< StorageConfiguration >  config = ref< StorageConfiguration >::create(Arena::debug());
    ref< LogicComponentStorage > storage
        = ref< LogicComponentStorage >::create(Arena::debug(), config, motor_class< u32 >());

    return 0;
}
