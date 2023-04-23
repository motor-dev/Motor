/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/filesystem/folder.meta.hh>
#include <ioprocess.hh>

#include <motor/core/threads/thread.hh>

namespace Motor {

Folder::Folder()
    : m_lock()
    , m_files(Arena::filesystem())
    , m_folders(Arena::filesystem())
    , m_mounts(Arena::filesystem())
    , m_upToDate(false)
{
    IOProcess::IOContext::begin();
}

Folder::~Folder()
{
    IOProcess::IOContext::end();
}

weak< File > Folder::openFile(istring name)
{
    ScopedCriticalSection lock(m_lock);
    return openFileNoLock(name);
}

weak< File > Folder::openFile(const ifilename& name)
{
    ScopedCriticalSection lock(m_lock);
    return openFileNoLock(name);
}

weak< Folder > Folder::openFolder(istring name)
{
    ScopedCriticalSection lock(m_lock);
    return openFolderNoLock(name);
}

weak< Folder > Folder::openFolder(const ipath& name)
{
    ScopedCriticalSection lock(m_lock);
    return openFolderNoLock(name);
}

weak< File > Folder::openFileNoLock(istring name)
{
    for(const auto& it: m_files)
    {
        if(it.first == name) return it.second;
    }
    return {};
}

weak< File > Folder::openFileNoLock(ifilename name)
{
    istring s = name.pop_front();
    if(name.size() > 0)
    {
        weak< Folder > f = openFolderNoLock(s);
        if(f)
        {
            return f->openFileNoLock(name);
        }
        else
        {
            return {};
        }
    }
    else
    {
        return openFileNoLock(s);
    }
}

weak< Folder > Folder::openFolderNoLock(istring name)
{
    for(const auto& it: m_mounts)
    {
        if(it.first == name) return it.second;
    }
    for(const auto& it: m_folders)
    {
        if(it.first == name) return it.second;
    }
    return {};
}

weak< Folder > Folder::openFolderNoLock(ipath name)
{
    istring s = name.pop_front();
    if(name.size() > 0)
    {
        weak< Folder > f = openFolderNoLock(s);
        if(f)
        {
            return f->openFolderNoLock(name);
        }
        else
        {
            return {};
        }
    }
    else
    {
        return openFolderNoLock(s);
    }
}

void Folder::mount(istring name, ref< Folder > folder)
{
    ScopedCriticalSection lock(m_lock);
    for(minitl::vector< minitl::tuple< istring, ref< Folder > > >::const_iterator it
        = m_folders.begin();
        it != m_folders.end(); ++it)
    {
        if(it->first == name)
        {
            motor_warning_format(Log::fs(), "mounting filesystem hides folder {0}", name);
        }
    }
    for(auto& m_mount: m_mounts)
    {
        if(m_mount.first == name)
        {
            motor_warning_format(Log::fs(), "mounting filesystem will unmount filesystem {0}",
                                 name);
            m_mount.second = folder;
            return;
        }
    }
    m_mounts.push_back(minitl::make_tuple(name, folder));
}

void Folder::mount(ipath name, const ref< Folder >& folder)
{
    istring s = name.pop_front();
    if(name.size() > 0)
    {
        weak< Folder > f = openFolder(s);
        if(f)
        {
            f->mount(name, folder);
        }
        else
        {
            motor_error_format(Log::fs(),
                               "could not mount folder; path {0} does not exist in the file system",
                               name);
        }
    }
    else
    {
        mount(s, folder);
    }
}

void Folder::umount(istring name)
{
    ScopedCriticalSection lock(m_lock);
    for(minitl::vector< minitl::tuple< istring, ref< Folder > > >::iterator it = m_mounts.begin();
        it != m_mounts.end(); ++it)
    {
        if(it->first == name)
        {
            minitl::swap(*it, m_mounts.back());
            m_mounts.pop_back();
            return;
        }
    }
    motor_error_format(Log::fs(), "could not unmount folder; path {0} is not mounted", name);
}

void Folder::umount(ipath name)
{
    istring s = name.pop_front();
    if(name.size() > 0)
    {
        weak< Folder > f = openFolder(s);
        if(f)
        {
            f->umount(name);
        }
        else
        {
            motor_error_format(
                Log::fs(), "could not unmount folder; path {0} does not exist in the file system",
                name);
        }
    }
    else
    {
        umount(s);
    }
}

void Folder::refresh(Folder::ScanPolicy scanPolicy)
{
    if(!m_upToDate)
    {
        doRefresh(scanPolicy);
        m_upToDate = true;
    }
}

void Folder::doRefresh(ScanPolicy scanPolicy)
{
    if(scanPolicy == Folder::ScanRecursive)
    {
        ScopedCriticalSection lock(m_lock);
        for(auto& m_folder: m_folders)
        {
            m_folder.second->refresh(scanPolicy);
        }
    }
}

}  // namespace Motor
