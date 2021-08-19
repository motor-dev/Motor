/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_ILOADER_HH_
#define MOTOR_RESOURCE_ILOADER_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/resource/description.script.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ResourceManager;

class motor_api(RESOURCE) ILoader : public minitl::refcountable
{
    friend class ResourceManager;
    friend class Description;
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

    virtual void load(weak< const Description > description, Resource & resource) = 0;
    virtual void reload(weak< const Description > oldDescription,
                        weak< const Description > newDescription, Resource & resource)
        = 0;
    virtual void unload(Resource & resource) = 0;

    virtual void onTicketUpdated(weak< const Description > /*description*/, Resource& /*resource*/,
                                 const minitl::Allocator::Block< u8 >& /*buffer*/, u32 /*progress*/,
                                 LoadType /*loadType*/)
    {
    }
    virtual void onTicketLoaded(weak< const Description > /*description*/, Resource& /*resource*/,
                                const minitl::Allocator::Block< u8 >& /*buffer*/,
                                LoadType /*loadType*/)
    {
        motor_notreached();
    }
};

}}  // namespace Motor::Resource

/**************************************************************************************************/
#endif
