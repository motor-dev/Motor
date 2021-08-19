/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_FILESYSTEM_WATCHQUEUE_HH_
#define MOTOR_FILESYSTEM_WATCHQUEUE_HH_
/**************************************************************************************************/
#include <motor/filesystem/stdafx.h>
#include <motor/core/threads/thread.hh>
#include <motor/filesystem/diskfolder.script.hh>
#include <motor/kernel/interlocked.hh>
#include <watchpoint.hh>

#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>

namespace Motor { namespace FileSystem {

class FileSystemWatchProcessQueue : public minitl::pointer
{
private:
    CFStringRef          m_Path;
    Thread               m_thread;
    iptr< CFRunLoopRef > m_runLoop;

private:
    static intptr_t runFileSystemWatch(intptr_t p1, intptr_t p2);
    static void     onFileSystemEvent(ConstFSEventStreamRef streamRef, void* clientCallBackInfo,
                                      size_t numEvents, void* eventPaths,
                                      const FSEventStreamEventFlags eventFlags[],
                                      const FSEventStreamEventId    eventIds[]);

public:
    FileSystemWatchProcessQueue();
    ~FileSystemWatchProcessQueue();

    ref< DiskFolder::Watch > addFolder(weak< DiskFolder > folder, const Motor::ipath& path);
};

}}  // namespace Motor::FileSystem

/**************************************************************************************************/
#endif
