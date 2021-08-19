/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MOTOR_SCRIPTENGINE_HH_
#define MOTOR_MOTOR_SCRIPTENGINE_HH_
/**************************************************************************************************/
#include <motor/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/script.script.hh>

namespace Motor {

template < typename T >
class ScriptEngine : public Resource::ILoader
{
protected:
    minitl::Allocator&                m_scriptArena;
    weak< Resource::ResourceManager > m_manager;

public:
    virtual ~ScriptEngine();

protected:
    ScriptEngine(minitl::Allocator& arena, weak< Resource::ResourceManager > manager);
    virtual void runBuffer(weak< const T > script, Resource::Resource& resource,
                           const minitl::Allocator::Block< u8 >& buffer)
        = 0;
    virtual void reloadBuffer(weak< const T > script, Resource::Resource& resource,
                              const minitl::Allocator::Block< u8 >& buffer)
        = 0;

private:
    virtual void load(weak< const Resource::Description > script,
                      Resource::Resource&                 resource) override;
    virtual void reload(weak< const Resource::Description > oldScript,
                        weak< const Resource::Description > newScript,
                        Resource::Resource&                 resource) override;
    virtual void onTicketLoaded(weak< const Resource::Description >   script,
                                Resource::Resource&                   resource,
                                const minitl::Allocator::Block< u8 >& buffer,
                                ILoader::LoadType                     type) override;
};

}  // namespace Motor

#include <motor/scriptengine.inl>

/**************************************************************************************************/
#endif
