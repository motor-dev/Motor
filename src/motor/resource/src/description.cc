/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>
#include <motor/resource/idescription.meta.hh>
#include <motor/resource/loader.hh>

namespace Motor { namespace Resource {

IDescription::IDescription() : m_resourceCount(0), m_resourceCache()
{
}

IDescription::~IDescription()
{
    Resource* resources = getResourceBuffer();
    for(u32 i = 0; i < m_resourceCount; ++i)
    {
        resources[i].~Resource();
    }
    if(m_resourceCount > MaxResourceCount)
    {
        Arena::resource().free(resources);
    }
}

void IDescription::load(const weak< ILoader >& loader) const
{
    Resource* resources = getResourceBuffer();
    if(++m_resourceCount > MaxResourceCount)
    {
        u64   bufferSize     = m_resourceCount * sizeof(Resource);
        auto* resourceBuffer = static_cast< Resource* >(Arena::resource().alloc(bufferSize));
        for(u32 i = 0; i < m_resourceCount - 1; ++i)
        {
            new(&resourceBuffer[i]) Resource(minitl::move(resources[i]));
            resources[i].~Resource();
        }
        if(m_resourceCount > MaxResourceCount + 1)
        {
            Arena::resource().free(resources);
        }
        m_resourceCache.m_resourcePointer = resources = resourceBuffer;
    }
    new(&resources[m_resourceCount - 1]) Resource;
    resources[m_resourceCount - 1].m_owner = loader->m_id;
    loader->load(this, resources[m_resourceCount - 1]);
}

void IDescription::unload(const weak< ILoader >& loader) const
{
    Resource* resources = getResourceBuffer();
    for(u32 i = 0; i < m_resourceCount; ++i)
    {
        if(resources[i].m_owner == loader->m_id)
        {
            loader->unload(this, resources[i]);
            resources[i] = minitl::move(resources[m_resourceCount - 1]);
            resources[m_resourceCount - 1].~Resource();
            --m_resourceCount;
            Resource* newBuffer = getResourceBuffer();
            if(newBuffer != resources)
            {
                for(u32 j = 0; j < m_resourceCount; ++j)
                {
                    new(&newBuffer[j]) Resource(minitl::move(resources[j]));
                    resources[j].~Resource();
                }
                Arena::resource().free(resources);
            }
            return;
        }
    }
    motor_notreached();
}

Resource& IDescription::getResourceForWriting(const weak< const ILoader >& owner) const
{
    Resource* resources = getResourceBuffer();
    for(u32 i = 0; i < m_resourceCount; ++i)
    {
        if(resources[i].m_owner == owner->m_id)
        {
            return resources[i];
        }
    }
    return Resource::null();
}

const Resource& IDescription::getResource(const weak< const ILoader >& owner) const
{
    Resource* resources = getResourceBuffer();
    for(u32 i = 0; i < m_resourceCount; ++i)
    {
        if(resources[i].m_owner == owner->m_id)
        {
            return resources[i];
        }
    }
    return Resource::null();
}

Resource* IDescription::getResourceBuffer() const
{
    if(m_resourceCount <= MaxResourceCount)
    {
        return reinterpret_cast< Resource* >(m_resourceCache.m_resourceBuffer);
    }
    else
    {
        return m_resourceCache.m_resourcePointer;
    }
}

}}  // namespace Motor::Resource
