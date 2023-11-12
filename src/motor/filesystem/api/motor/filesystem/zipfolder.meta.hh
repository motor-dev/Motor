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
    friend class ZipFile;

private:
    class Handle : minitl::pointer
    {
    private:
        void* m_handle;

    public:
        explicit Handle(void* handle);
        ~Handle() override;

        operator void*()  // NOLINT(google-explicit-constructor)
        {
            return m_handle;
        }
        bool operator!() const
        {
            return m_handle == nullptr;
        }
    };
    ref< Handle > m_handle;
    ipath         m_path;

private:
    void doRefresh(Folder::ScanPolicy scanPolicy) override;
    void onChanged() override;

public:
    [[motor::meta(export = no)]] ZipFolder(const ref< Handle >& handle, const ipath& path,
                                           Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);

public:
    explicit ZipFolder(const ipath& zippath, const ipath& subFolder = ipath(),
                       Folder::ScanPolicy scanPolicy = Folder::ScanRecursive);
    ~ZipFolder() override;
};

}  // namespace Motor

#endif
