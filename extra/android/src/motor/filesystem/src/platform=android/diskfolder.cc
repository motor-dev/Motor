/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/diskfolder.meta.hh>
#include <motor/filesystem/zipfolder.meta.hh>
#include <posix/file.hh>
#include <watchpoint.hh>
#include <zipfile.hh>

#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unzip.h>

extern MOTOR_IMPORT const char* s_packagePath;

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
            perror("");
        }
    }
}

DiskFolder::DiskFolder(const ipath& diskpath, Folder::ScanPolicy scanPolicy,
                       Folder::CreatePolicy createPolicy)
    : m_path(diskpath)
    , m_handle()
    , m_index(m_path[0] == istring("apk:") ? 1 : 0)
    , m_watch()
{
    if(m_index == 0)
    {
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
    }
    else
    {
        ipath package_path = m_path;
        package_path.pop_front();
        zlib_filefunc_def_s defs {};
        fill_fopen_filefunc(&defs);
        m_handle.ptrHandle = unzOpen2(s_packagePath, &defs);
        if(!m_handle.ptrHandle)
        {
            motor_error_format(Log::fs(), "Could not open directory {0}/", m_path);
        }
    }

    if(scanPolicy != Folder::ScanNone)
    {
        refresh(scanPolicy);
    }
}

DiskFolder::~DiskFolder()
{
    ScopedCriticalSection lock(m_lock);
    if(m_index == 0)
    {
        if(m_handle.ptrHandle)
        {
            closedir((DIR*)m_handle.ptrHandle);
            m_handle.ptrHandle = nullptr;
        }
    }
    else
    {
        if(m_handle.ptrHandle)
        {
            unzClose(m_handle.ptrHandle);
            m_handle.ptrHandle = nullptr;
        }
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
        if(m_index == 0)
        {
            rewinddir((DIR*)m_handle.ptrHandle);
            while(dirent* d = readdir((DIR*)m_handle.ptrHandle))
            {
                if(d->d_name[0] == '.' && d->d_name[1] == 0) continue;
                if(d->d_name[0] == '.' && d->d_name[1] == '.' && d->d_name[2] == 0) continue;
                auto  name = istring(d->d_name);
                ipath p    = m_path;
                p.push_back(name);
                ipath::Filename filename = p.str();
                struct stat     s
                {
                };
                stat(filename.name, &s);
                if(errno == 0)
                {
                    motor_error_format(Log::fs(), "could not stat file {0}: {1}({2})",
                                       filename.name, strerror(errno), errno);
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
                        Arena::filesystem(), ipath(m_path) + ifilename(name), s.st_size,
                        s.st_mtime);
                    m_files.emplace_back(name, minitl::move(newFile));
                }
            }
        }
        else
        {
            ipath relativePath = m_path;
            relativePath.pop_front();
            if(unzGoToFirstFile(m_handle.ptrHandle) == UNZ_OK)
            {
                minitl::vector< istring > subdirs(Arena::stack());
                do
                {
                    unz_file_info info;
                    char          filepath[4096];
                    unzGetCurrentFileInfo(m_handle.ptrHandle, &info, filepath, sizeof(filepath),
                                          nullptr, 0, nullptr, 0);
                    ipath   path(filepath);
                    istring filename = path.pop_back();
                    if(path == relativePath)
                    {
                        unz_file_pos filePos;
                        unzGetFilePos(m_handle.ptrHandle, &filePos);
                        ifilename fullFilename = path + ifilename(filename);
                        m_files.emplace_back(filename, ref< ZipFile >::create(
                                                           Arena::filesystem(), m_handle.ptrHandle,
                                                           fullFilename, info, filePos));
                    }
                    else if(path.size() >= 1)
                    {
                        istring directory = path.pop_back();
                        if(relativePath == path)
                        {
                            subdirs.push_back(directory);
                        }
                    }
                } while(unzGoToNextFile(m_handle.ptrHandle) == UNZ_OK);

                for(minitl::vector< istring >::const_iterator it = subdirs.begin();
                    it != subdirs.end(); ++it)
                {
                    if(openFolderNoLock(ipath(*it)) == weak< Folder >())
                    {
                        ipath path = relativePath;
                        path.push_back(*it);
                        m_folders.emplace_back(*it, ref< ZipFolder >::create(Arena::filesystem(),
                                                                             m_handle.ptrHandle,
                                                                             path, newPolicy));
                    }
                }
            }
        }
    }
}

weak< File > DiskFolder::createFile(const istring& name)
{
    if(m_index == 0)
    {
        if(motor_assert(m_path[0] != istring("apk:"),
                        "can't create a file in the Package directory"))
            return {};
        ifilename::Filename path = (m_path + ifilename(name)).str();
        struct stat         s
        {
        };
        errno   = 0;
        FILE* f = fopen(path.name, "w");
        if(f == nullptr)
        {
            motor_error_format(Log::fs(), "could not create file {0}: {1}({2})", path.name,
                               strerror(errno), errno);
            return {};
        }
        fclose(f);
        if(stat(path.name, &s) != 0)
        {
            motor_error_format(Log::fs(), "could not create file {0}: {1}({2})", path.name,
                               strerror(errno), errno);
            return {};
        }

        ScopedCriticalSection lock(m_lock);
        scoped< File >        file = scoped< PosixFile >::create(
            Arena::filesystem(), m_path + ifilename(name), s.st_size, s.st_mtime);
        weak< File > result = file;

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
    else
    {
        motor_error(Log::fs(), "can't create new file: read-only APK filesystem");
        return {};
    }
}

void DiskFolder::onChanged()
{
}

}  // namespace Motor
