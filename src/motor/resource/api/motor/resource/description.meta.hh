/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_DESCRIPTION_META_HH_
#define MOTOR_RESOURCE_DESCRIPTION_META_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ILoader;
class ResourceManager;

class motor_api(RESOURCE) Description
    : public minitl::refcountable
    , public minitl::intrusive_list< const Description, 2 >::item
{
    friend class ResourceManager;
    MOTOR_NOCOPY(Description);

private:
    enum
    {
        MaxResourceCount = 2
    };
    union ResourceCache
    {
        Resource* m_resourcePointer;
        u8        m_resourceBuffer[MaxResourceCount * sizeof(Resource)];
    };
    mutable u32           m_resourceCount;
    mutable ResourceCache m_resourceCache;

private:
    Resource* getResourceBuffer() const;
    Resource& getResourceForWriting(weak< const ILoader > owner) const;
    void      load(weak< ILoader > loader) const;
    void      unload(weak< ILoader > loader) const;

protected:
    Description();
    ~Description();

public:
    const Resource& getResource(weak< const ILoader > owner) const;
};

}}  // namespace Motor::Resource

/**************************************************************************************************/
#endif
