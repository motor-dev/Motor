/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/zipfolder.meta.hh>
#include <zipfile.hh>

#include <unzip.h>

namespace Motor {

ZipFolder::Handle::Handle(void* handle) : m_handle(handle)
{
}

ZipFolder::Handle::~Handle()
{
    if(m_handle)
    {
        unzClose(m_handle);
        m_handle = nullptr;
    }
}

ZipFolder::ZipFolder(const ref< Handle >& handle, const ipath& path, Folder::ScanPolicy scanPolicy)
    : m_handle(handle)
    , m_path(path)
{
    motor_info_format(Log::fs(), "opening zip folder {0}", path);
    if(scanPolicy != Folder::ScanNone)
    {
        refresh(scanPolicy);
    }
}

ZipFolder::ZipFolder(const ipath& zippath, const ipath& folderPath, Folder::ScanPolicy scanPolicy)
    : m_handle(ref< Handle >::create(Arena::filesystem(), unzOpen(zippath.str().name)))
    , m_path(folderPath)
{
    if(!m_handle)
    {
        motor_error_format(Log::fs(), "Could not open zip {0}/", zippath);
    }

    if(scanPolicy != Folder::ScanNone)
    {
        refresh(scanPolicy);
    }
}

ZipFolder::~ZipFolder() = default;

void ZipFolder::doRefresh(Folder::ScanPolicy scanPolicy)
{
    Folder::doRefresh(scanPolicy);
    Folder::ScanPolicy newPolicy
        = (scanPolicy == Folder::ScanRecursive) ? Folder::ScanRecursive : Folder::ScanNone;
    if(m_handle)
    {
        ScopedCriticalSection lock(m_lock);
        if(unzGoToFirstFile(*m_handle) == UNZ_OK)
        {
            minitl::vector< istring > subdirs(Arena::stack());
            do
            {
                unz_file_info info;
                char          filepath[4096];
                unzGetCurrentFileInfo(*m_handle, &info, filepath, sizeof(filepath), nullptr, 0,
                                      nullptr, 0);
                ipath   path(filepath);
                istring filename = path.pop_back();
                if(path == m_path)
                {
                    unz_file_pos filePos;
                    unzGetFilePos(*m_handle, &filePos);
                    ifilename fullFilePath = path + ifilename(filename);
                    m_files.emplace_back(filename,
                                         scoped< ZipFile >::create(Arena::filesystem(), m_handle,
                                                                   fullFilePath, info, filePos));
                }
                else if(path.size() >= 1)
                {
                    istring directory = path.pop_back();
                    if(m_path == path)
                    {
                        subdirs.push_back(directory);
                    }
                }
            } while(unzGoToNextFile(*m_handle) == UNZ_OK);

            for(minitl::vector< istring >::const_iterator it = subdirs.begin(); it != subdirs.end();
                ++it)
            {
                if(openFolderNoLock(ipath(*it)) == weak< Folder >())
                {
                    ipath path = m_path;
                    path.push_back(*it);
                    m_folders.emplace_back(
                        *it,
                        ref< ZipFolder >::create(Arena::filesystem(), m_handle, path, newPolicy));
                }
            }
        }
    }
}

void ZipFolder::onChanged()
{
}

}  // namespace Motor
