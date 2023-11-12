/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_LOADER_HH
#define MOTOR_RESOURCE_LOADER_HH

#include <motor/resource/stdafx.h>
#include <motor/resource/description.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ResourceManager;

class motor_api(RESOURCE) ILoader : public minitl::pointer
{
    friend class ResourceManager;
    friend class IDescription;

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
    ~ILoader() override;

    virtual void load(const weak< const IDescription >& description, Resource& resource)   = 0;
    virtual void unload(const weak< const IDescription >& description, Resource& resource) = 0;
    virtual void reload(const weak< const IDescription >& oldDescription,
                        const weak< const IDescription >& newDescription, Resource& resource)
    {
        unload(oldDescription, resource);
        load(newDescription, resource);
    }

    virtual void onTicketUpdated(
        const weak< const IDescription >& /*description*/, Resource& /*resource*/,
        const minitl::allocator::block< u8 >& /*buffer*/, u32 /*progress*/, LoadType /*loadType*/)
    {
    }
    virtual void onTicketLoaded(
        const weak< const IDescription >& /*description*/, Resource& /*resource*/,
        const minitl::allocator::block< u8 >& /*buffer*/, LoadType /*loadType*/)
    {
        motor_notreached();
    }
};

}}  // namespace Motor::Resource

#endif
