/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/string/istring.hh>
#include <motor/core/threads/criticalsection.hh>
#include <motor/minitl/hashmap.hh>
#include <motor/minitl/tuple.hh>
#include <motor/minitl/utility.hh>
#include <motor/minitl/vector.hh>

namespace Motor {

enum LogLevel
{
    logDebug   = 0,
    logInfo    = 1,
    logWarning = 2,
    logError   = 3,
    logFatal   = 4
};

class Logger;

class ILogListener : public minitl::refcountable
{
    friend class Logger;

protected:
    static motor_api(CORE) const char* getLogLevelName(LogLevel level);
    ~ILogListener() override = default;
    virtual bool log(const inamespace& logname, LogLevel level, const char* filename, int line,
                     const char* thread, const char* msg) const
        = 0;
};

class motor_api(CORE) Logger : public minitl::refcountable
{
    friend class minitl::ref< Logger >;
    friend struct ScopedLogListener;

private:
    CriticalSection                                   m_cs;
    minitl::vector< minitl::weak< ILogListener > >    m_listeners;
    minitl::hashmap< istring, minitl::ref< Logger > > m_children;
    minitl::weak< Logger >                            m_parent;
    inamespace                                        m_name;
    LogLevel                                          m_logFilter;

private:
    Logger();
    Logger(const minitl::weak< Logger >& parent, const istring& name,
           LogLevel minLogLevel = logDebug);

public:
    ~Logger() override;

    minitl::ref< Logger >         getChild(const istring& name);
    static minitl::weak< Logger > instance(const inamespace& name);
    static minitl::ref< Logger >  root();

    inline bool willLog(LogLevel level) const
    {
        return level >= m_logFilter;
    }
    inline bool log(LogLevel level, const char* filename, int line, const char* msg) const
    {
        if(level >= m_logFilter)
        {
            return doLog(level, m_name, filename, line, msg);
        }
        return false;
    }

private:
    void addListener(const minitl::weak< ILogListener >& listener);
    void removeListener(const minitl::weak< ILogListener >& listener);
    bool doLog(LogLevel level, const inamespace& logName, const char* filename, int line,
               const char* msg) const;
};

struct ScopedLogListener
{
private:
    minitl::scoped< ILogListener > const m_listener {};

public:
    explicit ScopedLogListener(minitl::scoped< ILogListener >&& listener)
        : m_listener(minitl::move(listener))
    {
        motor_forceuse(this);
        Logger::root()->addListener(m_listener);
    }
    ~ScopedLogListener()
    {
        motor_forceuse(this);
        Logger::root()->removeListener(m_listener);
    }
    ScopedLogListener(const ScopedLogListener&) = delete;
};

#define motor_log(logger, level, msg)                                                              \
    do                                                                                             \
    {                                                                                              \
        const weak< ::Motor::Logger >& motor_log_ll = logger;                                      \
        if(motor_log_ll->willLog(level)) motor_log_ll->log(level, "", MOTOR_LINE, msg);            \
    } while(0)

#define motor_log_format(logger, level, msg, ...)                                                  \
    do                                                                                             \
    {                                                                                              \
        const weak< ::Motor::Logger >& motor_log_ll = logger;                                      \
        if(motor_log_ll->willLog(level))                                                           \
            motor_log_ll->log(level, MOTOR_FILE, MOTOR_LINE,                                       \
                              minitl::format< 4096 >(FMT(msg), __VA_ARGS__));                      \
    } while(0)

#if defined(_DEBUG)
#    define motor_debug(logger, msg) motor_log(logger, ::Motor::logDebug, msg)
#    define motor_debug_format(logger, msg, ...)                                                   \
        motor_log_format(logger, ::Motor::logDebug, msg, __VA_ARGS__)
#else
#    define motor_debug(logger, msg)             (void)0
#    define motor_debug_format(logger, msg, ...) (void)0
#endif

#define motor_info(logger, msg) motor_log(logger, ::Motor::logInfo, msg)
#define motor_info_format(logger, msg, ...)                                                        \
    motor_log_format(logger, ::Motor::logInfo, msg, __VA_ARGS__)

#define motor_warning(logger, msg) motor_log(logger, ::Motor::logWarning, msg)
#define motor_warning_format(logger, msg, ...)                                                     \
    motor_log_format(logger, ::Motor::logWarning, msg, __VA_ARGS__)

#define motor_error(logger, msg) motor_log(logger, ::Motor::logError, msg)
#define motor_error_format(logger, msg, ...)                                                       \
    motor_log_format(logger, ::Motor::logError, msg, __VA_ARGS__)

#define motor_fatal(logger, msg) motor_log(logger, ::Motor::logFatal, msg)
#define motor_fatal_format(logger, msg, ...)                                                       \
    motor_log_format(logger, ::Motor::logFatal, msg, __VA_ARGS__)

}  // namespace Motor
