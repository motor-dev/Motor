/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/resource/stdafx.h>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/resource/resource.hh>

namespace Motor { namespace Resource {

class ILoader;
class ResourceManager;

class motor_api(RESOURCE) IDescription
    : public minitl::refcountable
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
