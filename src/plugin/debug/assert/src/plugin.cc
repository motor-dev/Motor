/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Debug {

minitl::assertion_result assertionCallback(const char* file, int line, const char* expr,
                                           const char* message);
class AssertSetup : public minitl::refcountable
{
private:
    minitl::assertion_callback_t m_previousAssertionCallback;

public:
    AssertSetup(const AssertSetup& other)            = delete;
    AssertSetup& operator=(const AssertSetup& other) = delete;

    explicit AssertSetup(const Motor::Plugin::Context& /*context*/)
        : m_previousAssertionCallback(minitl::set_assertion_callback(&assertionCallback))
    {
        motor_debug(Log::system(), "installed assert callback");
    }
    ~AssertSetup() override
    {
        minitl::set_assertion_callback(m_previousAssertionCallback);
    }
};

}}  // namespace Motor::Debug

MOTOR_PLUGIN_REGISTER(Motor::Debug::AssertSetup)
