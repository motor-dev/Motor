/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MOTOR_SCRIPTENGINE_HH
#define MOTOR_MOTOR_SCRIPTENGINE_HH

#include <motor/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/script.hh>

namespace Motor {

template < typename T >
class ScriptEngine : public Resource::ILoader
{
protected:
    minitl::allocator&                m_scriptArena;
    weak< Resource::ResourceManager > m_manager;

public:
    ~ScriptEngine() override;

protected:
    ScriptEngine(minitl::allocator& arena, const weak< Resource::ResourceManager >& manager);
    virtual void runBuffer(const weak< const T >& script, Resource::Resource& resource,
                           const minitl::allocator::block< u8 >& buffer)
        = 0;
    virtual void reloadBuffer(const weak< const T >& script, Resource::Resource& resource,
                              const minitl::allocator::block< u8 >& buffer)
        = 0;

private:
    void load(const weak< const Resource::IDescription >& script,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldScript,
                const weak< const Resource::IDescription >& newScript,
                Resource::Resource&                         resource) override;
    void onTicketLoaded(const weak< const Resource::IDescription >& script,
                        Resource::Resource& resource, const minitl::allocator::block< u8 >& buffer,
                        ILoader::LoadType type) override;
};

}  // namespace Motor

#include <motor/scriptengine.inl>

#endif
