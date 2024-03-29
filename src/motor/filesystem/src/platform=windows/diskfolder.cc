/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/diskfolder.meta.hh>
#include <windows/file.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor {

static u64 getTimeStamp(FILETIME time)
{
    return u64(time.dwLowDateTime) + (u64(time.dwHighDateTime) << 32);
}

static void createDirectory(const ipath& path, Folder::CreatePolicy policy)
{
    motor_assert(policy != Folder::CreateNone, "invalid policy given to createDirectory");
    if(policy == Folder::CreateRecursive)
    {
        ipath parent = path;
        parent.pop_back();
        createDirectory(parent, policy);
    }
    ipath::Filename pathname = path.str('\\');
    if(!CreateDirectoryA(pathname.name, nullptr))
    {
        DWORD err = GetLastError();
        if(err == ERROR_ALREADY_EXISTS)
        {
            return;
        }
        else
        {
            motor_info_format(Log::fs(), "directory {0} could not be created: error code {1}",
                              pathname.name, err);
        }
    }
}

static i_u32 s_diskIndex = i_u32::create(0);

DiskFolder::DiskFolder(const ipath& diskpath, Folder::ScanPolicy scanPolicy,
                       Folder::CreatePolicy createPolicy)
    : m_path(diskpath)
    , m_handle()
    , m_index(s_diskIndex++)
{
    if(createPolicy != Folder::CreateNone)
    {
        createDirectory(diskpath, createPolicy);
    }
    ipath::Filename pathname = m_path.str('\\');
    m_handle.ptrHandle       = CreateFileA(pathname.name, GENERIC_READ,
                                           FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                                           nullptr, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, nullptr);
    if(m_handle.ptrHandle == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(), "Directory {0} could not be opened: ({1})", pathname.name,
                          errorCode);
    }

    if(scanPolicy != Folder::ScanNone)
    {
        refresh(scanPolicy);
    }
}

DiskFolder::~DiskFolder()
{
    CloseHandle(m_handle.ptrHandle);
}

void DiskFolder::doRefresh(Folder::ScanPolicy scanPolicy)
{
    Folder::doRefresh(scanPolicy);
    if(m_handle.ptrHandle)
    {
        WIN32_FIND_DATAA    data;
        ifilename::Filename pathname = (m_path + ifilename("*")).str('\\');
        HANDLE              h        = FindFirstFileA(pathname.name, &data);
        if(h != INVALID_HANDLE_VALUE)
        {
            do
            {
                if(data.cFileName[0] == '.' && data.cFileName[1] == 0) continue;
                if(data.cFileName[0] == '.' && data.cFileName[1] == '.' && data.cFileName[2] == 0)
                    continue;
                istring name = istring(data.cFileName);
                if(data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
                {
                    for(auto& m_folder: m_folders)
                    {
                        if(m_folder.first == name)
                        {
                            continue;
                        }
                    }
                    m_folders.emplace_back(
                        name, ref< DiskFolder >::create(Arena::filesystem(), m_path + ipath(name),
                                                        scanPolicy, Folder::CreateNone));
                }
                else
                {
                    u64 size = data.nFileSizeHigh;
                    size <<= 32;
                    size += data.nFileSizeLow;
                    scoped< Win32File > newFile
                        = scoped< Win32File >::create(Arena::filesystem(), m_path + ifilename(name),
                                                      size, getTimeStamp(data.ftLastWriteTime));
                    m_files.emplace_back(name, minitl::move(newFile));
                }
            } while(FindNextFileA(h, &data));
            FindClose(h);
        }
    }
}

weak< File > DiskFolder::createFile(const istring& name)
{
    const ifilename::Filename path = (m_path + ifilename(name)).str('\\');
    HANDLE h = CreateFileA(path.name, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, 0, nullptr);
    if(h == INVALID_HANDLE_VALUE)
    {
        DWORD errorCode = ::GetLastError();
        motor_info_format(Log::fs(),
                          "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                          m_path, path.name, errorCode);
        return {};
    }
    else
    {
        CloseHandle(h);
        WIN32_FIND_DATAA data;
        h = FindFirstFileA(path.name, &data);
        if(h == INVALID_HANDLE_VALUE)
        {
            DWORD errorCode = ::GetLastError();
            motor_info_format(
                Log::fs(), "file {0} ({1}) could not be opened: CreateFile returned an error ({2})",
                m_path, path.name, errorCode);
            return {};
        }
        FindClose(h);
        scoped< File > file = scoped< Win32File >::create(
            Arena::filesystem(), m_path + ifilename(name), 0, getTimeStamp(data.ftLastWriteTime));
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
}

void DiskFolder::onChanged()
{
    if(m_handle.ptrHandle)
    {
        WIN32_FIND_DATAA    data;
        ifilename::Filename pathname = (m_path + ifilename("*")).str('\\');
        HANDLE              h        = FindFirstFileA(pathname.name, &data);
        if(h != INVALID_HANDLE_VALUE)
        {
            do
            {
                if(data.cFileName[0] == '.' && data.cFileName[1] == 0) continue;
                if(data.cFileName[0] == '.' && data.cFileName[1] == '.' && data.cFileName[2] == 0)
                    continue;
                istring name = istring(data.cFileName);
                if(data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
                {
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
                        m_folders.emplace_back(name, ref< DiskFolder >::create(
                                                         Arena::filesystem(), m_path + ipath(name),
                                                         Folder::ScanNone, Folder::CreateNone));
                    }
                }
                else
                {
                    bool exists = false;
                    for(auto& m_file: m_files)
                    {
                        if(m_file.first == name)
                        {
                            exists   = true;
                            u64 size = data.nFileSizeHigh;
                            size <<= 32;
                            size += data.nFileSizeLow;
                            motor_checked_cast< Win32File >(m_file.second)
                                ->refresh(size, getTimeStamp(data.ftLastWriteTime));
                            break;
                        }
                    }
                    if(!exists)
                    {
                        u64 size = data.nFileSizeHigh;
                        size <<= 32;
                        size += data.nFileSizeLow;
                        scoped< Win32File > newFile = scoped< Win32File >::create(
                            Arena::filesystem(), m_path + ifilename(name), size,
                            getTimeStamp(data.ftLastWriteTime));
                        m_files.emplace_back(name, minitl::move(newFile));
                    }
                }
            } while(FindNextFileA(h, &data));
            FindClose(h);
        }
    }
}

}  // namespace Motor
