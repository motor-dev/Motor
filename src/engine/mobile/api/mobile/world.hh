/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_MOBILE_WORLD_HH_
#define BE_MOBILE_WORLD_HH_
/*****************************************************************************/
#include    <graphics/world.hh>
#include    <graphics/scene/scene.hh>
#include    <physics/world.hh>
#include    <sound/world.hh>

namespace BugEngine
{

class be_api(MOBILE) World : public Object
{
private:
    ref<Graphics::World>         m_graphicsSystem;
    ref<Physics::World>          m_physicsSystem;
    ref<Sound::World>            m_soundSystem;
public:
    World(float3 worldExtents);
    ~World();

    ref<BaseTask>    m_task;

    void createView(Graphics::WindowFlags f, ref<Graphics::Scene> scene);

    be_metaclass(MOBILE,World,Object)
    be_properties
        be_property(GraphicSystem)
            [be_read(m_graphicsSystem)]
            [be_write(m_graphicsSystem)];

        be_property(PhysicsSystem)
            [be_read(m_physicsSystem)]
            [be_write(m_physicsSystem)];

        be_property(SoundSystem)
            [be_read(m_soundSystem)]
            [be_write(m_soundSystem)];
    be_end
};

}


/*****************************************************************************/
#endif
