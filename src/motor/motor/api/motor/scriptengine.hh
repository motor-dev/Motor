/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/script.hh>

namespace Motor {

template < typename T >
class ScriptEngine : public Resource::ILoader
{
protected:
    minitl::Allocator&                m_scriptArena;
    weak< Resource::ResourceManager > m_manager;

public:
    ~ScriptEngine() override;

protected:
    ScriptEngine(minitl::Allocator& arena, weak< Resource::ResourceManager > manager);
    virtual void runBuffer(const weak< const T >& script, Resource::Resource& resource,
                           const minitl::Allocator::Block< u8 >& buffer)
        = 0;
    virtual void reloadBuffer(const weak< const T >& script, Resource::Resource& resource,
                              const minitl::Allocator::Block< u8 >& buffer)
        = 0;

private:
    void load(const weak< const Resource::IDescription >& script,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldScript,
                const weak< const Resource::IDescription >& newScript,
                Resource::Resource&                         resource) override;
    void onTicketLoaded(const weak< const Resource::IDescription >& script,
                        Resource::Resource& resource, const minitl::Allocator::Block< u8 >& buffer,
                        ILoader::LoadType type) override;
};

}  // namespace Motor

#include <motor/scriptengine.inl>
