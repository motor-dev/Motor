/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/resource/stdafx.h>
#include <motor/resource/description.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ResourceManager;

class motor_api(RESOURCE) ILoader : public minitl::refcountable
{
    friend class ResourceManager;
    friend class IDescription;
    MOTOR_NOCOPY(ILoader);

public:
    enum FileType
    {
        FileText,
        FileBinary
    };
    enum LoadType
    {
        LoadFirstTime,
        LoadReload
    };

protected:
    const u32 m_id;

protected:
    ILoader();
    ~ILoader();

    virtual void load(weak< const IDescription > description, Resource & resource)   = 0;
    virtual void unload(weak< const IDescription > description, Resource & resource) = 0;
    virtual void reload(weak< const IDescription > oldDescription,
                        weak< const IDescription > newDescription, Resource & resource)
    {
        unload(oldDescription, resource);
        load(newDescription, resource);
    }

    virtual void onTicketUpdated(weak< const IDescription > /*description*/, Resource& /*resource*/,
                                 const minitl::Allocator::Block< u8 >& /*buffer*/, u32 /*progress*/,
                                 LoadType /*loadType*/)
    {
    }
    virtual void onTicketLoaded(weak< const IDescription > /*description*/, Resource& /*resource*/,
                                const minitl::Allocator::Block< u8 >& /*buffer*/,
                                LoadType /*loadType*/)
    {
        motor_notreached();
    }
};

}}  // namespace Motor::Resource
