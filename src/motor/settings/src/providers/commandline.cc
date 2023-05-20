/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/settings/stdafx.h>
#include <motor/minitl/utility.hh>
#include <motor/reflection/valueparse.hh>
#include <motor/settings/providers/commandline.hh>

namespace Motor { namespace Settings {

minitl::hashmap< istring, SettingsProvider::SettingsList >
CommandLineSettingsProvider::buildSettings(int argc, const char* argv[])
{
    minitl::hashmap< istring, SettingsProvider::SettingsList > result(Arena::temporary());
    static const char*                                         s_true = "true";
    for(int i = 1; i < argc; ++i)
    {
        if(argv[i][0] == '-')
        {
            const char* nameBegin = argv[i] + 1;
            const char* sep       = nameBegin;
            const char* nameEnd   = nameBegin;
            const char* optionBegin;
            while(*nameEnd && *nameEnd != '=')
            {
                if(*nameEnd == '.') sep = nameEnd;
                ++nameEnd;
            }
            if(*nameEnd == '=')
            {
                optionBegin = nameEnd + 1;
            }
            else if(i + 1 < argc)
            {
                if(*argv[i + 1] == '-')
                {
                    optionBegin = s_true;
                }
                else
                {
                    ++i;
                    optionBegin = argv[i];
                }
            }
            else
            {
                optionBegin = s_true;
            }
            const char* optionEnd = optionBegin;
            while(*optionEnd)
                ++optionEnd;
            if(sep == nameBegin)
            {
                motor_error_format(Log::settings(), "invalid command line option: {0}", nameBegin);
                continue;
            }
            else
            {
                Meta::AST::MessageList errorList(Arena::stack());
                istring                category(nameBegin, sep);
                istring                property(sep + 1, nameEnd);
                ref< Meta::AST::Node > value
                    = Meta::parseValue(Arena::script(), errorList, optionBegin, optionEnd, 0, 0);
                for(Meta::AST::MessageList::const_iterator it = errorList.begin();
                    it != errorList.end(); ++it)
                {
                    Log::settings()->log(logError, "<command line>", 0, it->message);
                }
                if(errorList.empty()) addSetting(result, category, property, value);
            }
        }
    }
    return result;
}

CommandLineSettingsProvider::CommandLineSettingsProvider(int argc, const char* argv[],
                                                         const ref< Folder >& folder)
    : SettingsProvider(minitl::move(buildSettings(argc, argv)), folder)
{
}

CommandLineSettingsProvider::~CommandLineSettingsProvider() = default;

void CommandLineSettingsProvider::log(const Meta::AST::Message& message) const
{
    Log::settings()->log(message.severity, "<command line>", 0, message.message);
}

}}  // namespace Motor::Settings
