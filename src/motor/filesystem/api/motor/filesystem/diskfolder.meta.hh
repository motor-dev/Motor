/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_DISKFOLDER_META_HH
#define MOTOR_FILESYSTEM_DISKFOLDER_META_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/folder.meta.hh>

namespace Motor {

class motor_api(FILESYSTEM) DiskFolder : public Folder
{
private:
    union Handle
    {
        void* ptrHandle;
        u64   intHandle;
    };
    ipath  m_path;
    Handle m_handle;
    u32    m_index;

private:
    void doRefresh(Folder::ScanPolicy scanPolicy) override;
    void onChanged() override;

public:
    explicit DiskFolder(const ipath&         diskpath,
                        Folder::ScanPolicy   scanPolicy   = Folder::ScanRecursive,
                        Folder::CreatePolicy createPolicy = Folder::CreateOne);
    ~DiskFolder() override;

    weak< File > createFile(const istring& name);
};

}  // namespace Motor

#include <motor/filesystem/diskfolder.meta.factory.hh>
#endif
