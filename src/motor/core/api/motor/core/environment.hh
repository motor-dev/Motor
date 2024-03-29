/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_ENVIRONMENT_HH
#define MOTOR_CORE_ENVIRONMENT_HH

#include <motor/core/stdafx.h>

namespace Motor {

class motor_api(CORE) Environment
{
private:
    Environment();
    ~Environment();

private:
    ipath     m_homeDirectory;
    ipath     m_dataDirectory;
    istring   m_game;
    istring   m_user;
    ifilename m_programPath;

private:
    static ipath canonicalPath(const char* path, const char* pathSeparators);

public:
    static Environment& getEnvironment();

    void init();
    void init(int argc, const char* argv[]);

    const ipath& getHomeDirectory() const
    {
        return m_homeDirectory;
    }
    ipath getGameHomeDirectory() const
    {
        return m_homeDirectory + ipath(m_game);
    }
    const ipath& getDataDirectory() const
    {
        return m_dataDirectory;
    }
    const istring& getGame() const
    {
        return m_game;
    }
    const istring& getUser() const
    {
        return m_user;
    }
    const ifilename& getProgramPath() const
    {
        return m_programPath;
    }
    static const char* getEnvironmentVariable(const char* variable);
    static size_t      getProcessorCount();
};

}  // namespace Motor

#endif
