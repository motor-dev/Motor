/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_ZIPFOLDER_SCRIPT_HH_
#define MOTOR_FILESYSTEM_ZIPFOLDER_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/folder.script.hh>

namespace Motor {

class FileSystemWatch;

class motor_api(FILESYSTEM) ZipFolder : public Folder
{
private:
    void* m_handle;
    ipath m_path;

private:
    void doRefresh(Folder::ScanPolicy scanPolicy) override;
    void onChanged() override;

public:
    ZipFolder(void* handle, ipath path, Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
published:
    ZipFolder(const ipath& zippath, Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
    ~ZipFolder();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
