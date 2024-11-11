/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/diskfolder.meta.hh>
#include <sys/stat.h>
#include <sys/types.h>
#include DIRENT_H
#include <errno.h>
#include <limits.h>
#include <posix/file.hh>
#include <stdio.h>

namespace Motor {

static void createDirectory(const ipath& path, Folder::CreatePolicy policy)
{
    motor_assert(policy != Folder::CreateNone, "invalid policy given to createDirectory");
    if(policy == Folder::CreateRecursive)
    {
        ipath parent = path;
        parent.pop_back();
        createDirectory(parent, policy);
    }
    ipath::Filename p = path.str();
    if(mkdir(p.name, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH) == -1)
    {
        if(errno != EEXIST)
        {
            perror(nullptr);
        }
    }
}

DiskFolder::DiskFolder(const ipath& diskpath, Folder::ScanPolicy scanPolicy,
                       Folder::CreatePolicy createPolicy)
    : m_path(diskpath)
    , m_handle()
    , m_index(0)
{
    motor_forceuse(m_index);
    if(createPolicy != Folder::CreateNone)
    {
        createDirectory(diskpath, createPolicy);
    }
    ipath::Filename pathname = m_path.str();
    m_handle.ptrHandle       = opendir(pathname.name);
    if(!m_handle.ptrHandle)
    {
        motor_error_format(Log::fs(), "Could not open directory {0}: {1}", diskpath,
                           strerror(errno));
    }

    if(scanPolicy != Folder::ScanNone)
    {
        refresh(scanPolicy);
    }
}

DiskFolder::~DiskFolder()
{
    ScopedCriticalSection lock(m_lock);
    if(m_handle.ptrHandle)
    {
        closedir((DIR*)m_handle.ptrHandle);
        m_handle.ptrHandle = nullptr;
    }
}

void DiskFolder::doRefresh(Folder::ScanPolicy scanPolicy)
{
    Folder::doRefresh(scanPolicy);
    Folder::ScanPolicy newPolicy
        = (scanPolicy == Folder::ScanRecursive) ? Folder::ScanRecursive : Folder::ScanNone;
    if(m_handle.ptrHandle)
    {
        ScopedCriticalSection lock(m_lock);
        rewinddir((DIR*)m_handle.ptrHandle);
        while(dirent* d = readdir((DIR*)m_handle.ptrHandle))
        {
            if(strcmp(d->d_name, ".") == 0) continue;
            if(strcmp(d->d_name, "..") == 0) continue;
            auto  name = istring(d->d_name);
            ipath p    = m_path;
            p.push_back(name);
            ipath::Filename filename = p.str();
            struct stat     s        = {};
            stat(filename.name, &s);
            if(errno == 0)
            {
                motor_error_format(Log::fs(), "could not stat file {0}: {1}({2})", filename.name,
                                   strerror(errno), errno);
            }
            else if(s.st_mode & S_IFDIR)
            {
                ref< DiskFolder > newFolder = ref< DiskFolder >::create(
                    Arena::filesystem(), p, newPolicy, Folder::CreateNone);
                m_folders.emplace_back(name, newFolder);
            }
            else
            {
                scoped< File > newFile = scoped< PosixFile >::create(
                    Arena::filesystem(), ipath(m_path) + ifilename(name), s.st_size, s.st_mtime);
                m_files.emplace_back(name, minitl::move(newFile));
            }
        }
    }
}

weak< File > DiskFolder::createFile(const istring& name)
{
    struct stat s = {};
    errno         = 0;
    char  fullPathBuffer[PATH_MAX];
    char* fullPath = realpath(m_path.str().name, fullPathBuffer);
    if(!fullPath)
    {
        motor_error_format(Log::fs(), "could not get real path of {0}: {1}({2})", m_path,
                           strerror(errno), errno);
        return {};
    }
    strcat(fullPath, "/");
    strcat(fullPath, name.c_str());
    FILE* f = fopen(fullPath, "w");
    if(f == nullptr)
    {
        motor_error_format(Log::fs(), "could not create file {0}: {1}({2})", fullPath,
                           strerror(errno), errno);
        return {};
    }
    fclose(f);
    if(stat(fullPath, &s) != 0)
    {
        motor_error_format(Log::fs(), "could not create file {0}: {1}({2})", fullPath,
                           strerror(errno), errno);
        return {};
    }

    ScopedCriticalSection lock(m_lock);
    scoped< File > file = scoped< PosixFile >::create(Arena::filesystem(), m_path + ifilename(name),
                                                      s.st_size, s.st_mtime);
    weak< File >   result = file;

    for(auto& m_file: m_files)
    {
        if(m_file.first == name)
        {
            m_file.second = minitl::move(file);
            return result;
        }
    }
    m_files.emplace_back(name, minitl::move(file));
    return result;
}

void DiskFolder::onChanged()
{
    if(m_handle.ptrHandle)
    {
        ScopedCriticalSection lock(m_lock);
        rewinddir((DIR*)m_handle.ptrHandle);
        while(dirent* d = readdir((DIR*)m_handle.ptrHandle))
        {
            if(strcmp(d->d_name, ".") == 0) continue;
            if(strcmp(d->d_name, "..") == 0) continue;
            auto  name = istring(d->d_name);
            ipath p    = m_path;
            p.push_back(name);
            ipath::Filename filename = p.str();
            struct stat     s        = {};
            int             result   = stat(filename.name, &s);
            if(result != 0)
            {
                motor_error_format(Log::fs(), "could not stat file {0}: {1}({2})", filename.name,
                                   strerror(errno), errno);
            }
            else if(s.st_mode & S_IFDIR)
            {
                /* TODO: deleted folder */
                bool exists = false;

                for(auto& m_folder: m_folders)
                {
                    if(m_folder.first == name)
                    {
                        exists = true;
                        break;
                    }
                }
                if(!exists)
                {
                    motor_info_format(Log::fs(), "new folder: {0}", p);
                    ref< DiskFolder > newFolder = ref< DiskFolder >::create(
                        Arena::filesystem(), p, Folder::ScanNone, Folder::CreateNone);
                    m_folders.emplace_back(name, newFolder);
                }
            }
            else
            {
                /* TODO: deleted file */
                bool exists = false;

                for(auto& m_file: m_files)
                {
                    if(m_file.first == name)
                    {
                        motor_checked_cast< PosixFile >(m_file.second)
                            ->refresh(s.st_size, s.st_mtime);
                        exists = true;
                    }
                }
                if(!exists)
                {
                    motor_info_format(Log::fs(), "new file: {0}", p);
                    scoped< File > newFile = scoped< PosixFile >::create(
                        Arena::filesystem(), ipath(m_path) + ifilename(name), s.st_size,
                        s.st_mtime);
                    m_files.emplace_back(name, minitl::move(newFile));
                }
            }
        }
    }
}

}  // namespace Motor
