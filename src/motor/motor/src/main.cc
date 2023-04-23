/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>
#include <motor/main.hh>
#include <settings.meta.hh>

#include <motor/core/environment.hh>
#include <motor/filesystem/diskfolder.meta.hh>
#include <motor/meta/engine/namespace.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>
#include <motor/settings/providers/commandline.hh>

#include <cstdio>
#include <cstdlib>
#include <unistd.h>

#ifdef MOTOR_PLATFORM_WIN32
/* todo: move to separate file */
#    define WIN32_LEAN_AND_MEAN
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#    include <windows.h>

#endif

namespace {

class FileLogListener : public Motor::ILogListener
{
private:
    weak< Motor::File > m_logFile;

public:
    explicit FileLogListener(const weak< Motor::File >& file) : m_logFile(file)
    {
    }
    ~FileLogListener() override = default;

protected:
    bool log(const Motor::inamespace& logname, Motor::LogLevel level, const char* filename,
             int line, const char* thread, const char* msg) const override
    {
        if(Motor::MainSettings::Log::get().enableFileLog)
        {
            const minitl::format_buffer< 1024u > message
                = minitl::format< 1024u >(FMT("{0}:{1} ({2})\t({3}:{4}) {5}\n"), filename, line,
                                          logname.str().name, getLogLevelName(level), thread, msg);
            const char* str = message.c_str();
            // TODO: does not appear to be threadsafe at all
            m_logFile->beginWrite(str, motor_checked_numcast< u32 >(strlen(str)));
        }
        return true;
    }
};

class ConsoleLogListener : public Motor::ILogListener
{
private:
    Motor::LogLevel m_minimumLogLevel;

public:
    explicit ConsoleLogListener(Motor::LogLevel minimumLogLevel)
        : m_minimumLogLevel(minimumLogLevel)
    {
    }
    ~ConsoleLogListener() override = default;

protected:
    bool log(const Motor::inamespace& logname, Motor::LogLevel level, const char* filename,
             int line, const char* thread, const char* msg) const override
    {
        if(level >= m_minimumLogLevel)
        {
            if(Motor::MainSettings::Log::get().enableConsoleLog)
            {
                using namespace Motor;
#ifdef MOTOR_PLATFORM_WIN32
                minitl::format_buffer< 1024u > message = minitl::format< 1024u >(
                    FMT("{0}({1}): {2}\t({3}) {4}{5}"), filename, line, logname,
                    getLogLevelName(level), msg, (msg[strlen(msg) - 1] == '\n' ? "" : "\n"));
                OutputDebugString(message);
#    define isatty(x) 1
#endif
                static const char* term = Environment::getEnvironmentVariable("TERM");
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
                case logDebug: color = colors[2]; break;
                case logInfo: color = colors[3]; break;
                case logWarning: color = colors[4]; break;
                case logError: color = colors[5]; break;
                case logFatal: color = colors[6]; break;
                default: break;
                }

                const char* normal = colors[0];
                fprintf(stdout, "[%s%s%s] %s%s(%s)%s %s(%d): %s", color, getLogLevelName(level),
                        normal, colors[1], logname.str().name, thread, normal, filename, line, msg);
                fflush(stdout);
                motor_forceuse(filename);
                motor_forceuse(line);
                if(msg[strlen(msg) - 1] != '\n') fprintf(stdout, "\n");
            }
        }
        return true;
    }
};
}  // namespace

int beMain(int argc, const char* argv[])
{
    using namespace Motor;
    Environment::getEnvironment().init(argc, argv);
#if MOTOR_ENABLE_EXCEPTIONS
    try
#endif
    {
        ref< DiskFolder > root = ref< DiskFolder >::create(
            Arena::general(), Environment::getEnvironment().getHomeDirectory(),
            DiskFolder::ScanRecursive, DiskFolder::CreateOne);
        ScopedLogListener console(
            scoped< ConsoleLogListener >::create(Arena::debug(), Motor::logInfo));
        ref< DiskFolder > home = ref< DiskFolder >::create(
            Arena::general(), Environment::getEnvironment().getGameHomeDirectory(),
            DiskFolder::ScanRecursive, DiskFolder::CreateOne);

        Settings::CommandLineSettingsProvider settings(argc, argv, home);
        Plugin::Plugin< minitl::pointer >     platformAssert(
            inamespace("plugin.debug.assert"),
            Plugin::Context(weak< Resource::ResourceManager >(), ref< Folder >(),
                                weak< Scheduler >()));
        ScopedLogListener file(
            scoped< FileLogListener >::create(Arena::debug(), home->createFile("log")));
        scoped< Scheduler >                 scheduler = scoped< Scheduler >::create(Arena::task());
        scoped< Resource::ResourceManager > manager
            = scoped< Resource::ResourceManager >::create(Arena::resource());

        Plugin::Plugin< Application > app(inamespace(Environment::getEnvironment().getGame()),
                                          Plugin::Context(manager, home, scheduler));
        if(app)
        {
            motor_info_format(Log::motor(), "running {0}", Environment::getEnvironment().getGame());
            return app->run();
        }
        else
        {
            motor_error_format(Log::motor(), "failed to load main module \"{0}\", exiting",
                               Environment::getEnvironment().getGame());
            return EXIT_FAILURE;
        }
    }
#if MOTOR_ENABLE_EXCEPTIONS
    catch(...)
    {
        return EXIT_FAILURE;
    }
#endif
}
