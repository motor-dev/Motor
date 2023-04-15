#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/core/environment.hh>
#include <motor/core/logger.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <unistd.h>

#ifdef MOTOR_PLATFORM_WIN32

#    define WIN32_LEAN_AND_MEAN
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#    include <windows.h>

#endif

class ConsoleLogListener : public Motor::ILogListener
{
private:
    minitl::AssertionCallback_t m_previousCallback;

public:
    ConsoleLogListener()
    {
        m_previousCallback = minitl::setAssertionCallback(&onAssert);
    }
    ~ConsoleLogListener()
    {
        minitl::setAssertionCallback(m_previousCallback);
    }

private:
    static minitl::AssertionResult onAssert(const char* file, int line, const char* expr,
                                            const char* message)
    {
        motor_fatal_format(Motor::Logger::root(), "{0}:{1} Assertion failed: {2}\n\t{3}", file,
                           line, expr, message);
        return minitl::AssertionResult::Break;
    }

protected:
    virtual bool log(const Motor::inamespace& logname, Motor::LogLevel level, const char* filename,
                     int line, const char* thread, const char* msg) const override
    {
#ifdef MOTOR_PLATFORM_WIN32
        minitl::format_buffer< 1024u > message = minitl::format< 1024u >(
            FMT("{0}({1}): {2}\t({3}) {4}{5}"), filename, line, logname, getLogLevelName(level),
            msg, (msg[strlen(msg) - 1] == '\n' ? "" : "\n"));
        OutputDebugString(message);
#    define isatty(x) 1
#endif
        static const char* term
            = Motor::Environment::getEnvironment().getEnvironmentVariable("TERM");
        static const char* colors[]
            = {isatty(1) && term ? "\x1b[0m" : "",   isatty(1) && term ? "\x1b[01;1m" : "",
               isatty(1) && term ? "\x1b[36m" : "",  isatty(1) && term ? "\x1b[32m" : "",
               isatty(1) && term ? "\x1b[33m" : "",  isatty(1) && term ? "\x1b[31m" : "",
               isatty(1) && term ? "\x1b[1;31m" : ""};
#ifdef MOTOR_PLATFORM_WIN32
#    undef isatty
#endif
        const char* color = colors[0];
        switch(level)
        {
        case Motor::logDebug: color = colors[2]; break;
        case Motor::logInfo: color = colors[3]; break;
        case Motor::logWarning: color = colors[4]; break;
        case Motor::logError: color = colors[5]; break;
        case Motor::logFatal: color = colors[6]; break;
        default: break;
        }

        const char* normal = colors[0];
        fprintf(stdout, "[%s%s%s] %s%s(%s)%s: %s", color, getLogLevelName(level), normal, colors[1],
                logname.str().name, thread, normal,
                // filename, line,
                msg);
        fflush(stdout);
        motor_forceuse(filename);
        motor_forceuse(line);
        if(msg[strlen(msg) - 1] != '\n') fprintf(stdout, "\n");
        return true;
    }
};

Motor::ScopedLogListener console(scoped< ConsoleLogListener >::create(Motor::Arena::debug()));

extern "C" MOTOR_EXPORT void initpy_motor()
{
    using namespace Motor;
    using namespace Motor::Python;
    /* python 2.x module initialisation */
    Environment::getEnvironment().init();
    motor_info(Log::python(), "loading module py_motor (Python 2)");
    static ref< PythonLibrary > s_loadedLibrary
        = ref< PythonLibrary >::create(Arena::general(), (const char*)0);
    setCurrentContext(s_loadedLibrary);
    init2_py_motor(false);
}

extern "C" MOTOR_EXPORT Motor::Python::PyObject* PyInit_py_motor()
{
    using namespace Motor;
    using namespace Motor::Python;
    /* python 3.x module initialisation */
    Environment::getEnvironment().init();
    static ref< PythonLibrary > s_loadedLibrary
        = ref< PythonLibrary >::create(Arena::general(), (const char*)0);
    setCurrentContext(s_loadedLibrary);
    motor_info(Log::python(), "loading module py_motor (Python 3)");
    PyObject* module = init3_py_motor(false);
    return module;
}
