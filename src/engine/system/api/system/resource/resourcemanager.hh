/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_SYSTEM_RESOURCE_RESOURCEMANAGER_HH_
#define BE_SYSTEM_RESOURCE_RESOURCEMANAGER_HH_
/*****************************************************************************/
#include    <minitl/ptr/refcountable.hh>
#include    <system/resource/resource.script.hh>
#include    <system/file/file.script.hh>

namespace BugEngine
{

class be_api(SYSTEM) ResourceManager : public minitl::pointer
{
    BE_NOCOPY(ResourceManager);
private:
    struct LoaderInfo
    {
        raw<const RTTI::ClassInfo>  classinfo;
        weak<IResourceLoader>       loader;
    };
    struct Ticket
    {
        weak<IResourceLoader>   loader;
        weak<const Resource>    resource;
        ref<const File::Ticket> ticket;
        u32                     progress;
    };
private:
    minitl::vector<LoaderInfo>  m_loaders;
    minitl::vector<Ticket>      m_tickets;
public:
    ResourceManager();
    ~ResourceManager();

    void attach(raw<const RTTI::ClassInfo> classinfo, weak<IResourceLoader> loader);
    void detach(raw<const RTTI::ClassInfo> classinfo, weak<const IResourceLoader> loader);
    void load(raw<const RTTI::ClassInfo> classinfo, weak<const Resource> resource) const;
    void unload(raw<const RTTI::ClassInfo> classinfo, weak<const Resource> resource) const;

    template< typename T > void attach(weak<IResourceLoader> loader)        { attach(be_typeid<T>::klass(), loader); }
    template< typename T > void detach(weak<const IResourceLoader> loader)  { detach(be_typeid<T>::klass(), loader); }
    template< typename T > void load(weak<T> resource) const                { load(be_typeid<T>::klass(), resource); }
    template< typename T > void load(ref<T> resource) const                 { load(be_typeid<T>::klass(), resource); }
    template< typename T > void unload(weak<T> resource) const              { unload(be_typeid<T>::klass(), resource); }
    template< typename T > void unload(ref<T> resource) const               { unload(be_typeid<T>::klass(), resource); }

    void addTicket(weak<IResourceLoader> loader, weak<const Resource> resource, weak<const File> file);
    void updateTickets();
};

}

/*****************************************************************************/
#endif
