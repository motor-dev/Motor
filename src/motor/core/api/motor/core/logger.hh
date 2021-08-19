/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_LOGGER_HH_
#define MOTOR_CORE_LOGGER_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/core/string/istring.hh>
#include <motor/minitl/hash_map.hh>
#include <motor/minitl/tuple.hh>
#include <motor/minitl/vector.hh>

namespace Motor {

enum LogLevel
{
    logSpam    = 0,
    logDebug   = 1,
    logInfo    = 2,
    logWarning = 3,
    logError   = 4,
    logFatal   = 5
};

class Logger;

class ILogListener : public minitl::refcountable
{
    friend class Logger;

protected:
    static motor_api(CORE) const char* getLogLevelName(LogLevel level);
    virtual ~ILogListener()
    {
    }
    virtual bool log(const istring& logname, LogLevel level, const char* filename, int line,
                     const char* thread, const char* msg) const = 0;
};

class motor_api(CORE) Logger : public minitl::refcountable
{
    friend class minitl::ref< Logger >;
    friend struct ScopedLogListener;
    MOTOR_NOCOPY(Logger);

private:
    minitl::vector< minitl::weak< ILogListener > >    m_listeners;
    minitl::hashmap< istring, minitl::ref< Logger > > m_children;
    minitl::weak< Logger >                            m_parent;
    istring                                           m_name;

private:
    Logger();

public:
    Logger(minitl::ref< Logger > parent, const istring& name);
    ~Logger();

    static minitl::ref< Logger > instance(const inamespace& name);
    static bool log(const inamespace& name, LogLevel level, const char* filename, int line,
                    const char* msg);
    static minitl::ref< Logger > root();

    bool log(LogLevel level, const char* filename, int line, const char* msg) const;

private:
    void addListener(minitl::weak< ILogListener > listener);
    void removeListener(minitl::weak< ILogListener > listener);
    bool doLog(LogLevel level, istring logName, const char* filename, int line, const char* msg)
        const;
};

struct ScopedLogListener
{
private:
    minitl::scoped< ILogListener > const m_listener;

public:
    ScopedLogListener(minitl::scoped< ILogListener > listener) : m_listener(listener)
    {
        Logger::root()->addListener(m_listener);
    }
    ~ScopedLogListener()
    {
        Logger::root()->removeListener(m_listener);
    }

private:
    ScopedLogListener(const ScopedLogListener&);
    ScopedLogListener& operator=(const ScopedLogListener&);
};

#define ALLDEBUG
#if defined(_DEBUG) || defined(ALLDEBUG)
#    define motor_spam(msg)                                                                        \
        ::Motor::Logger::root()->log(::Motor::logSpam, __FILE__, __LINE__,                         \
                                     (minitl::format< 1024u >)msg)
#    define motor_debug(msg)                                                                       \
        ::Motor::Logger::root()->log(::Motor::logDebug, __FILE__, __LINE__,                        \
                                     (minitl::format< 1024u >)msg)
#else
#    define motor_spam(msg)
#    define motor_debug(msg)
#endif

#if !defined(NDEBUG) || defined(ALLDEBUG)
#    define motor_info(msg)                                                                        \
        ::Motor::Logger::root()->log(::Motor::logInfo, __FILE__, __LINE__,                         \
                                     (minitl::format< 1024u >)msg)
#else
#    define motor_info(msg)
#endif

#define motor_warning(msg)                                                                         \
    ::Motor::Logger::root()->log(::Motor::logWarning, __FILE__, __LINE__,                          \
                                 (minitl::format< 1024u >)msg)
#define motor_error(msg)                                                                           \
    ::Motor::Logger::root()->log(::Motor::logError, __FILE__, __LINE__,                            \
                                 (minitl::format< 1024u >)msg)
#define motor_fatal(msg)                                                                           \
    ::Motor::Logger::root()->log(::Motor::logFatal, __FILE__, __LINE__,                            \
                                 (minitl::format< 1024u >)msg)

}  // namespace Motor

/**************************************************************************************************/
#endif
