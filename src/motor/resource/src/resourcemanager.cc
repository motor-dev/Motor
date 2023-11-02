/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/resource/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor { namespace Resource {

ResourceManager::LoaderInfo::LoaderInfo(raw< const Meta::Class > classinfo)
    : classinfo(classinfo)
    , loaders(Arena::resource())
    , resources()
{
}

ResourceManager::ResourceManager()
    : m_loaders(Arena::resource())
    , m_tickets(Arena::resource())
    , m_pendingTickets(Arena::resource())
    , m_watches(Arena::resource())
{
}

ResourceManager::~ResourceManager() = default;

weak< ResourceManager::LoaderInfo >
ResourceManager::getLoaderInfo(raw< const Meta::Class > classinfo)
{
    motor_assert_format(classinfo->interfaces, "Resource class {0} does not have an operator table",
                        classinfo->name);
    motor_assert_format(classinfo->interfaces->resourceType,
                        "Resource class {0} does not have a resource class", classinfo->name);
    raw< const Meta::Class > resourceType = classinfo->interfaces->resourceType;
    for(auto& m_loader: m_loaders)
    {
        if(resourceType == m_loader->classinfo) return m_loader;
    }
    m_loaders.push_back(ref< LoaderInfo >::create(Arena::resource(), resourceType));
    return m_loaders.back();
}

void ResourceManager::attach(raw< const Meta::Class > classinfo, const weak< ILoader >& loader)
{
    weak< LoaderInfo > info = getLoaderInfo(classinfo);
#if MOTOR_ENABLE_ASSERT
    for(auto& it: info->loaders)
    {
        if(motor_assert_format(it != loader, "registering twice the same loader for class {0}",
                               classinfo->name))
            return;
    }
#endif
    motor_info_format(Log::resource(), "registering loader for type {0}", classinfo->name);
    info->loaders.push_back(loader);
    for(const auto& resource: info->resources)
    {
        resource.load(loader);
    }
}

void ResourceManager::detach(raw< const Meta::Class >     classinfo,
                             const weak< const ILoader >& loader)
{
    for(auto& m_watch: m_watches)
    {
        if(m_watch.loader == loader)
        {
            m_watch.expired  = true;
            m_watch.file     = weak< const File >();
            m_watch.resource = weak< const IDescription >();
            m_watch.loader   = weak< ILoader >();
        }
    }
    weak< LoaderInfo > info = getLoaderInfo(classinfo);
    for(minitl::vector< weak< ILoader > >::iterator it = info->loaders.begin();
        it != info->loaders.end();)
    {
        if(*it == loader)
        {
            motor_info_format(Log::resource(), "unregistering loader for type {0}",
                              classinfo->name);
            for(const auto& resource: info->resources)
            {
                resource.unload(*it);
            }
            info->loaders.erase(it);
            return;
        }
        else
        {
            ++it;
        }
    }
    motor_error_format(Log::resource(), "loader was not in the list of loaders for type {0}",
                       classinfo->name);
}

void ResourceManager::load(raw< const Meta::Class >          classinfo,
                           const weak< const IDescription >& resource)
{
    weak< LoaderInfo > info = getLoaderInfo(classinfo);
    for(minitl::vector< weak< ILoader > >::const_iterator it = info->loaders.begin();
        it != info->loaders.end(); ++it)
    {
        resource->load(*it);
    }
    info->resources.push_back(*resource.operator->());
}

void ResourceManager::unload(raw< const Meta::Class >          classinfo,
                             const weak< const IDescription >& resource)
{
    resource->unhook();
    weak< LoaderInfo > info = getLoaderInfo(classinfo);
    for(minitl::vector< weak< ILoader > >::const_iterator it = info->loaders.begin();
        it != info->loaders.end(); ++it)
    {
        resource->unload(*it);
    }

    for(auto& m_watche: m_watches)
    {
        if(m_watche.resource == resource)
        {
            m_watche.expired  = true;
            m_watche.file     = weak< const File >();
            m_watche.resource = weak< const IDescription >();
            m_watche.loader   = weak< ILoader >();
        }
    }
}

void ResourceManager::addTicket(const weak< ILoader >&            loader,
                                const weak< const IDescription >& description,
                                const weak< const File >& file, ILoader::FileType fileType,
                                ILoader::LoadType loadType)
{
    Ticket ticket;
    ticket.loader    = loader;
    ticket.file      = file;
    ticket.resource  = description;
    ticket.ticket    = file->beginRead(0, 0, fileType == ILoader::FileText, Arena::temporary());
    ticket.fileState = file->getState();
    ticket.progress  = 0;
    ticket.fileType  = fileType;
    ticket.loadType  = loadType;
    ticket.expired   = false;
    m_pendingTickets.push_back(ticket);
}

size_t ResourceManager::updateTickets()
{
    size_t ticketCount = m_tickets.size();
    do
    {
        m_tickets.push_back(m_pendingTickets.begin(), m_pendingTickets.end());
        ticketCount += m_pendingTickets.size();
        m_pendingTickets.clear();

        for(minitl::vector< Ticket >::iterator it = m_tickets.begin(); it != m_tickets.end();
            /*nothing*/)
        {
            if(it->ticket->error)
            {
                motor_error(Log::resource(), "resource loading error");
                it = m_tickets.erase(it);
            }
            else if(it->ticket->done())
            {
                it->loader->onTicketLoaded(it->resource,
                                           it->resource->getResourceForWriting(it->loader),
                                           it->ticket->buffer, it->loadType);
                it->ticket = ref< const File::Ticket >();
                m_watches.push_back(*it);
                it = m_tickets.erase(it);
            }
            else if(it->ticket->processed != it->progress)
            {
                it->progress = it->ticket->processed;
                it->loader->onTicketUpdated(it->resource,
                                            it->resource->getResourceForWriting(it->loader),
                                            it->ticket->buffer, it->progress, it->loadType);
                ++it;
            }
            else
            {
                ++it;
            }
        }
    } while(!m_pendingTickets.empty());

    minitl::vector< Ticket > updatedTickets(Arena::temporary());
    for(minitl::vector< Ticket >::iterator it = m_watches.begin(); it != m_watches.end();
        /*nothing*/)
    {
        if(it->expired)
        {
            it = m_watches.erase(it);
        }
        else if(it->file->isDeleted())
        {
            motor_info(Log::resource(), "todo: file deleted, remove resource");
            it = m_watches.erase(it);
        }
        else if(it->file->getState() != it->fileState)
        {
            updatedTickets.push_back(*it);
            it = m_watches.erase(it);
        }
        else
        {
            ++it;
        }
    }

    for(auto& updatedTicket: updatedTickets)
    {
        updatedTicket.loader->reload(
            updatedTicket.resource, updatedTicket.resource,
            updatedTicket.resource->getResourceForWriting(updatedTicket.loader));
    }

    return ticketCount;
}

}}  // namespace Motor::Resource
