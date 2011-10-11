/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_SYSTEM_POSIX_FILE_HH_
#define BE_SYSTEM_POSIX_FILE_HH_
/*****************************************************************************/

namespace BugEngine
{

class PosixFile : public File
{
private:
    ifilename m_file;
public:
    PosixFile(ifilename file, File::Media media, u64 size);
    ~PosixFile();
private:
    void doFillBuffer(weak<File::Ticket> ticket) const override;
};

}

/*****************************************************************************/
#endif