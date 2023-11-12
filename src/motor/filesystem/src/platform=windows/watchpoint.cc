/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <diskwatch.hh>
#include <watchpoint.hh>

#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#    define NOMINMAX
#endif
#include <windows.h>

namespace Motor { namespace FileSystem {

#define MS_VC_EXCEPTION 0x406D1388
#pragma pack(push, 8)
struct THREADNAME_INFO
{
    DWORD  dwType {};
    LPCSTR szName {};
    DWORD  dwThreadID {};
    DWORD  dwFlags {};
};
#pragma pack(pop)

class WatchRequest : public knl::istack< WatchRequest >::node
{
    friend class WatchThread;

public:
    enum RequestType
    {
        Add,
        Remove
    };

private:
    ipath             m_path;
    ref< WatchPoint > m_watchpoint;

public:
    WatchRequest(RequestType /*type*/, const ipath& path, const ref< WatchPoint >& watchpoint)
        : m_path(path)
        , m_watchpoint(watchpoint)
    {
    }
};

class WatchThread : public minitl::pointer
{
private:
    static const u32 s_maximumWatchCount = MAXIMUM_WAIT_OBJECTS - 1;
    HANDLE           m_semaphore;
    minitl::vector< minitl::tuple< HANDLE, weak< FileSystem::WatchPoint > > > m_watches;
    knl::istack< WatchRequest >                                               m_requests;
    u32                                                                       m_watchCount;
    HANDLE                                                                    m_thread;

private:
    static unsigned long WINAPI doWatchFolders(void* params);

public:
    WatchThread();
    ~WatchThread() override;

    bool add(const ipath& path, const ref< FileSystem::WatchPoint >& watchpoint);
};

static void setThreadName(const istring& name)
{
#ifdef _MSC_VER
    THREADNAME_INFO info {};
    info.dwType     = 0x1000;
    info.szName     = name.c_str();
    info.dwThreadID = GetCurrentThreadId();
    info.dwFlags    = 0;
    __try
    {
        RaiseException(MS_VC_EXCEPTION, 0, sizeof(info) / sizeof(ULONG_PTR), (ULONG_PTR*)&info);
    }
    __except(EXCEPTION_EXECUTE_HANDLER)
    {
    }
#else
    motor_forceuse(name);
#endif
}

unsigned long WINAPI WatchThread::doWatchFolders(void* params)
{
    auto*        watchThread   = reinterpret_cast< WatchThread* >(params);
    static i_u32 s_threadIndex = i_u32::create(0);
    setThreadName(istring(minitl::format< 1024u >(FMT("FileSystem watch {0}"), s_threadIndex++)));

    while(true)
    {
        HANDLE handles[s_maximumWatchCount + 1];
        int    i     = 0;
        handles[i++] = watchThread->m_semaphore;
        for(minitl::vector<
                minitl::tuple< HANDLE, weak< FileSystem::WatchPoint > > >::const_iterator it
            = watchThread->m_watches.begin();
            it != watchThread->m_watches.end(); ++it)
        {
            handles[i++] = it->first;
        }
        DWORD result = WaitForMultipleObjects(1 + (DWORD)watchThread->m_watches.size(), handles,
                                              FALSE, INFINITE);
        if(result == WAIT_OBJECT_0)
        {
            WatchRequest* request = watchThread->m_requests.pop();
            if(!request)
            {
                break;
            }
            else
            {
                DWORD flags = FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME
                              | FILE_NOTIFY_CHANGE_ATTRIBUTES | FILE_NOTIFY_CHANGE_SIZE
                              | FILE_NOTIFY_CHANGE_LAST_WRITE;
                HANDLE handle
                    = FindFirstChangeNotificationA(request->m_path.str().name, FALSE, flags);
                watchThread->m_watches.emplace_back(handle, request->m_watchpoint);
                request->~WatchRequest();
                Arena::temporary().free(request);
            }
        }
        else if(result >= WAIT_OBJECT_0 + 1
                && result <= WAIT_OBJECT_0 + watchThread->m_watches.size())
        {
            int index = int(result - WAIT_OBJECT_0 - 1);
            watchThread->m_watches[index].second->signalDirty();
            FindNextChangeNotification(watchThread->m_watches[index].first);
        }
        else if(result >= WAIT_ABANDONED_0 + 1
                && result <= WAIT_ABANDONED_0 + watchThread->m_watches.size())
        {
            motor_notreached();
            int index = int(result - WAIT_ABANDONED_0 - 1);
            FindNextChangeNotification(watchThread->m_watches[index].first);
        }
        else
        {
            char* errorMessage = nullptr;
            DWORD errorCode    = ::GetLastError();
            FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, nullptr,
                          errorCode, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                          reinterpret_cast< LPSTR >(&errorMessage), 0, nullptr);
            motor_error_format(Log::fs(), "file watch wait interrupted: {0}", errorMessage);
            ::LocalFree(errorMessage);
            motor_notreached();
        }
    }
    return 0;
}

WatchThread::WatchThread()
    : m_semaphore(CreateSemaphore(nullptr, 0, 65535, nullptr))
    , m_watches(Arena::filesystem())
    , m_watchCount(0)
    , m_thread(CreateThread(
          nullptr, 0, reinterpret_cast< LPTHREAD_START_ROUTINE >(&WatchThread::doWatchFolders),
          this, 0, nullptr))
{
}

WatchThread::~WatchThread()
{
    ReleaseSemaphore(m_semaphore, 1, nullptr);
    DWORD result = WaitForSingleObject(m_thread, 2000);
    motor_assert(result != WAIT_TIMEOUT, "timed out when waiting for filesystem watch thread");
    motor_forceuse(result);
    CloseHandle(m_thread);
    CloseHandle(m_semaphore);
    for(auto& m_watche: m_watches)
    {
        FindCloseChangeNotification(m_watche.first);
    }
}

bool WatchThread::add(const ipath& path, const ref< FileSystem::WatchPoint >& watchpoint)
{
    if(m_watchCount < s_maximumWatchCount)
    {
        auto* request = new(Arena::temporary()) WatchRequest(WatchRequest::Add, path, watchpoint);
        m_requests.push(request);
        m_watchCount++;
        ReleaseSemaphore(m_semaphore, 1, nullptr);
        return true;
    }
    else
    {
        return false;
    }
}

ref< Folder::Watch > WatchPoint::addWatch(const weak< DiskFolder >& folder,
                                          const Motor::ipath&       path)
{
    static minitl::vector< ref< WatchThread > > s_threads(Arena::filesystem());

    ref< WatchPoint > watchpoint = getWatchPoint(path);
    if(!watchpoint)
    {
        watchpoint = getWatchPointOrCreate(path);
        bool found = false;
        for(auto& s_thread: s_threads)
        {
            if(s_thread->add(path, watchpoint))
            {
                found = true;
                break;
            }
        }
        if(!found)
        {
            ref< WatchThread > thread = ref< WatchThread >::create(Arena::filesystem());
            thread->add(path, watchpoint);
        }
    }
    ref< DiskFolder::Watch > result
        = ref< DiskFolder::Watch >::create(Arena::filesystem(), folder, watchpoint);
    return result;
}

}}  // namespace Motor::FileSystem
