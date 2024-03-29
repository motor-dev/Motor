/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_RESOURCE_RESOURCEMANAGER_HH
#define MOTOR_RESOURCE_RESOURCEMANAGER_HH

#include <motor/resource/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/vector.hh>
#include <motor/resource/idescription.meta.hh>
#include <motor/resource/loader.hh>

namespace Motor { namespace Resource {

class motor_api(RESOURCE) ResourceManager : public minitl::pointer
{
private:
    class LoaderInfo : public minitl::pointer
    {
    public:
        explicit LoaderInfo(raw< const Meta::Class > classinfo);

        raw< const Meta::Class > const                  classinfo;
        minitl::vector< weak< ILoader > >               loaders;
        minitl::intrusive_list< const IDescription, 2 > resources;
    };
    struct Ticket
    {
        weak< ILoader >            loader;
        weak< const IDescription > resource;
        weak< const File >         file;
        ref< const File::Ticket >  ticket;
        u64                        fileState;
        u32                        progress;
        ILoader::FileType          fileType;
        ILoader::LoadType          loadType;
        bool                       expired;
    };

private:
    minitl::vector< scoped< LoaderInfo > > m_loaders;
    minitl::vector< Ticket >               m_tickets;
    minitl::vector< Ticket >               m_pendingTickets;
    minitl::vector< Ticket >               m_watches;

private:
    weak< LoaderInfo > getLoaderInfo(raw< const Meta::Class > classinfo);

public:
    ResourceManager();
    ~ResourceManager() override;

    void attach(raw< const Meta::Class > classinfo, const weak< ILoader >& loader);
    void detach(raw< const Meta::Class > classinfo, const weak< const ILoader >& loader);
    void load(raw< const Meta::Class > classinfo, const weak< const IDescription >& resource);
    void unload(raw< const Meta::Class > classinfo, const weak< const IDescription >& resource);

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
    void load(const weak< const T >& resource)
    {
        load(motor_class< T >(), resource);
    }
    template < typename T >
    void unload(const weak< const T >& resource)
    {
        unload(motor_class< T >(), resource);
    }
    template < typename T >
    void load(const ref< const T >& resource)
    {
        load(motor_class< T >(), resource);
    }
    template < typename T >
    void unload(const ref< const T >& resource)
    {
        unload(motor_class< T >(), resource);
    }

    template < typename T >
    void load(const scoped< const T >& resource)
    {
        load(motor_class< T >(), resource);
    }
    template < typename T >
    void unload(const scoped< const T >& resource)
    {
        unload(motor_class< T >(), resource);
    }

    void   addTicket(const weak< ILoader >& loader, const weak< const IDescription >& description,
                     const weak< const File >& file, ILoader::FileType fileType,
                     ILoader::LoadType loadType);
    size_t updateTickets();
};

}}  // namespace Motor::Resource

#endif
