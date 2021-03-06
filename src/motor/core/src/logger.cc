/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/logger.hh>

#include <motor/core/threads/thread.hh>
#include <motor/minitl/scopedptr.hh>

namespace Motor {

static const char* s_logLevelNames[]
    = {" SPAM  ", " DEBUG ", " INFO  ", "WARNING", " ERROR ", " FATAL "};

motor_api(CORE) const char* ILogListener::getLogLevelName(LogLevel level)
{
    if(u32(level) <= logFatal)
        return s_logLevelNames[level];
    else
        return "Unknown";
}

Logger::Logger() : m_listeners(Arena::debug()), m_children(Arena::debug()), m_name("all")
{
}

Logger::Logger(ref< Logger > parent, const istring& name)
    : m_listeners(Arena::debug())
    , m_children(Arena::debug())
    , m_parent(parent)
    , m_name(name)
{
}

Logger::~Logger()
{
}

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

ref< Logger > Logger::instance(const inamespace& name)
{
    ref< Logger > result = root();

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

bool Logger::log(const inamespace& name, LogLevel level, const char* filename, int line,
                 const char* msg)
{
    return instance(name)->log(level, filename, line, msg);
}

void Logger::addListener(weak< ILogListener > listener)
{
    ScopedCriticalSection _(m_cs);
    m_listeners.push_back(listener);
}

void Logger::removeListener(weak< ILogListener > listener)
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
    motor_warning("unable to remove listener");
}

bool Logger::log(LogLevel level, const char* filename, int line, const char* msg) const
{
    return doLog(level, m_name, filename, line, msg);
}

bool Logger::doLog(LogLevel level, istring logName, const char* filename, int line,
                   const char* msg) const
{
    ScopedCriticalSection _(m_cs);
    bool                  result = false;
    for(minitl::vector< weak< ILogListener > >::const_iterator it = m_listeners.begin();
        it != m_listeners.end(); ++it)
    {
        result |= (*it)->log(logName, level, filename, line, Thread::name().c_str(), msg);
    }

    if(m_parent)
    {
        result |= m_parent->doLog(level, logName, filename, line, msg);
    }

    return result;
}

}  // namespace Motor
