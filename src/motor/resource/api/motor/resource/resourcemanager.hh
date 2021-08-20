/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_RESOURCE_RESOURCEMANAGER_HH_
#define MOTOR_RESOURCE_RESOURCEMANAGER_HH_
/**************************************************************************************************/
#include <motor/resource/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/minitl/array.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/resource/description.meta.hh>
#include <motor/resource/loader.hh>

namespace Motor { namespace Resource {

class motor_api(RESOURCE) ResourceManager : public minitl::pointer
{
    MOTOR_NOCOPY(ResourceManager);

private:
    struct LoaderInfo
    {
        LoaderInfo();
        raw< const Meta::Class >                       classinfo;
        minitl::vector< weak< ILoader > >              loaders;
        minitl::intrusive_list< const Description, 2 > resources;
    };
    struct Ticket
    {
        weak< ILoader >           loader;
        weak< const Description > resource;
        weak< const File >        file;
        ref< const File::Ticket > ticket;
        u64                       fileState;
        u32                       progress;
        ILoader::FileType         fileType;
        ILoader::LoadType         loadType;
        bool                      outdated;
    };

private:
    minitl::array< LoaderInfo > m_loaders;
    minitl::vector< Ticket >    m_tickets;
    minitl::vector< Ticket >    m_pendingTickets;
    minitl::vector< Ticket >    m_watches;

private:
    LoaderInfo& getLoaderInfo(raw< const Meta::Class > classinfo);

public:
    ResourceManager();
    ~ResourceManager();

    void attach(raw< const Meta::Class > classinfo, weak< ILoader > loader);
    void detach(raw< const Meta::Class > classinfo, weak< const ILoader > loader);
    void load(raw< const Meta::Class > classinfo, weak< const Description > resource);
    void unload(raw< const Meta::Class > classinfo, weak< const Description > resource);

    template < typename T >
    void attach(weak< ILoader > loader)
    {
        attach(motor_class< T >(), loader);
    }
    template < typename T >
    void detach(weak< const ILoader > loader)
    {
        detach(motor_class< T >(), loader);
    }
    template < typename T >
    void load(weak< const T > resource)
    {
        load(motor_class< T >(), resource);
    }
    template < typename T >
    void load(ref< const T > resource)
    {
        load(motor_class< T >(), resource);
    }
    template < typename T >
    void unload(weak< const T > resource)
    {
        unload(motor_class< T >(), resource);
    }
    template < typename T >
    void unload(ref< const T > resource)
    {
        unload(motor_class< T >(), resource);
    }

    void   addTicket(weak< ILoader > loader, weak< const Description > description,
                     weak< const File > file, ILoader::FileType fileType, ILoader::LoadType loadType);
    size_t updateTickets();
};

}}  // namespace Motor::Resource

/**************************************************************************************************/
#endif
