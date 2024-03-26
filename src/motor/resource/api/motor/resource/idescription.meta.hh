/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_IDESCRIPTION_META_HH
#define MOTOR_RESOURCE_IDESCRIPTION_META_HH

#include <motor/resource/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ILoader;
class ResourceManager;

class motor_api(RESOURCE) IDescription
    : public minitl::pointer
    , public minitl::intrusive_list< const IDescription, 2 >::item
{
    friend class ResourceManager;

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
    Resource& getResourceForWriting(const weak< const ILoader >& owner) const;
    void      load(const weak< ILoader >& loader) const;
    void      unload(const weak< ILoader >& loader) const;

protected:
    IDescription();
    ~IDescription() override;

public:
    const Resource& getResource(const weak< const ILoader >& owner) const;
};

}}  // namespace Motor::Resource

#include <motor/resource/idescription.meta.factory.hh>
#endif
