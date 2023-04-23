/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/application.hh>

#include <csignal>

namespace Motor {

static Application* s_application = nullptr;

extern "C" void signalHandler(int /*signal*/)
{
    // motor_info(Log::system(), "interrupted");
    if(s_application)
    {
        s_application->finish();
        s_application = nullptr;
    }
}

void Application::registerInterruptions()
{
    s_application = this;
    struct sigaction action
    {
    };
    memset(&action, 0, sizeof(action));
    action.sa_handler = &signalHandler;
    sigemptyset(&action.sa_mask);
    sigaddset(&action.sa_mask, SIGINT);
    action.sa_flags = SA_RESTART;
    sigaction(SIGINT, &action, nullptr);
    sigaddset(&action.sa_mask, SIGTERM);
    sigaction(SIGINT, &action, nullptr);
}

void Application::unregisterInterruptions()
{
    s_application = nullptr;
}

}  // namespace Motor
