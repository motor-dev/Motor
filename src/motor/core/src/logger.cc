/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/logger.hh>

#include <motor/core/threads/thread.hh>
#include <motor/minitl/scopedptr.hh>

namespace Motor {

static const char* s_logLevelNames[] = {" DEBUG ", " INFO  ", "WARNING", " ERROR ", " FATAL "};

motor_api(CORE) const char* ILogListener::getLogLevelName(LogLevel level)
{
    if(u32(level) <= logFatal)
        return s_logLevelNames[level];
    else
        return "Unknown";
}

Logger::Logger()
    : m_listeners(Arena::debug())
    , m_children(Arena::debug())
    , m_name()
    , m_logFilter(LogLevel::logWarning)
{
}

Logger::Logger(const weak< Logger >& parent, const istring& name, LogLevel minLogLevel)
    : m_listeners(Arena::debug())
    , m_children(Arena::debug())
    , m_parent(parent)
    , m_name(parent ? m_parent->m_name + name : inamespace(name))
    , m_logFilter(minLogLevel)
{
}

Logger::~Logger() = default;

ref< Logger > Logger::getChild(const istring& name)
{
    ScopedCriticalSection                               _(m_cs);
    minitl::hashmap< istring, ref< Logger > >::iterator it = m_children.find(name);
    if(it == m_children.end())
    {
        ref< Logger > next = ref< Logger >::create(Arena::debug(), this, name);
        m_children.insert(name, next);
        return next;
    }
    else
        return it->second;
}

weak< Logger > Logger::instance(const inamespace& name)
{
    weak< Logger > result = root();

    for(u32 i = 0; i < name.size(); ++i)
    {
        result = result->getChild(name[i]);
    }
    return result;
}

ref< Logger > Logger::root()
{
    static ref< Logger > s_rootLogger = ref< Logger >::create(Arena::debug());
    return s_rootLogger;
}

// bool Logger::log(const inamespace& name, LogLevel level, const char* filename, int line,
//                  const char* msg)
//{
//     return instance(name)->log(level, filename, line, msg);
// }

void Logger::addListener(const weak< ILogListener >& listener)
{
    ScopedCriticalSection _(m_cs);
    m_listeners.push_back(listener);
}

void Logger::removeListener(const weak< ILogListener >& listener)
{
    ScopedCriticalSection _(m_cs);
    for(minitl::vector< weak< ILogListener > >::iterator it = m_listeners.begin();
        it != m_listeners.end(); ++it)
    {
        if(*it == listener)
        {
            m_listeners.erase(it);
            return;
        }
    }
    motor_warning(Log::system(), "unable to remove listener: listener not found in list");
}

bool Logger::doLog(LogLevel level, const inamespace& logName, const char* filename, int line,
                   const char* msg) const
{
    ScopedCriticalSection _(m_cs);
    bool                  result = false;
    for(const auto& m_listener: m_listeners)
    {
        result |= m_listener->log(logName, level, filename, line, Thread::name().c_str(), msg);
    }

    if(m_parent)
    {
        result |= m_parent->doLog(level, logName, filename, line, msg);
    }

    return result;
}

namespace Log {

weak< Logger > motor()
{
    static weak< Logger > logger = Logger::root()->getChild(istring("motor"));
    return logger;
}

weak< Logger > system()
{
    static weak< Logger > logger = motor()->getChild(istring("system"));
    return logger;
}

weak< Logger > thread()
{
    static weak< Logger > logger = system()->getChild(istring("thread"));
    return logger;
}

}  // namespace Log

}  // namespace Motor
