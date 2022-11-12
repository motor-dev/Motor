/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    ipath canonicalPath(const char* path, const char* pathSeparators);

public:
    static Environment& getEnvironment();

    void init();
    void init(int argc, const char* argv[]);

    const ipath& getHomeDirectory() const
    {
        return m_homeDirectory;
    }
    const ipath getGameHomeDirectory() const
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
    const char* getEnvironmentVariable(const char* variable) const;
    size_t      getProcessorCount() const;
};

}  // namespace Motor
