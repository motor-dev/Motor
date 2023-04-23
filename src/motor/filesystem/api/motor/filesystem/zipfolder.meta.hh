/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    ZipFolder(void* handle, const ipath& path,
              Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
published:
    explicit ZipFolder(const ipath& zippath, Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
    ~ZipFolder() override;
};

}  // namespace Motor
