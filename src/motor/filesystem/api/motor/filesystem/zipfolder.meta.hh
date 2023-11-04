/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_FILESYSTEM_ZIPFOLDER_META_HH
#define MOTOR_FILESYSTEM_ZIPFOLDER_META_HH

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/folder.meta.hh>

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
    [[motor::meta(export = no)]] ZipFolder(void* handle, const ipath& path,
                                           Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);

public:
    explicit ZipFolder(const ipath& zippath, Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
    ~ZipFolder() override;
};

}  // namespace Motor

#endif
