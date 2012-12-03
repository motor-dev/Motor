/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_FILESYSTEM_FILE_DISKFOLDER_SCRIPT_HH_
#define BE_FILESYSTEM_FILE_DISKFOLDER_SCRIPT_HH_
/*****************************************************************************/
#include    <filesystem/folder.script.hh>

namespace BugEngine
{

class be_api(FILESYSTEM) DiskFolder : public Folder
{
private:
    union Handle
    {
        void*   ptrHandle;
        u64     intHandle;
    };
    ipath   m_path;
    Handle  m_handle;
    u32     m_index;
private:
    void doRefresh(Folder::ScanPolicy scanPolicy) override;
published:
    DiskFolder(const ipath& diskpath, Folder::ScanPolicy scanPolicy = Folder::ScanRecursive, Folder::CreatePolicy createPolicy = Folder::CreateOne);
    ~DiskFolder();

    weak<File> createFile(const istring& name);
};

}

/*****************************************************************************/
#endif