/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/module.hh>

namespace Motor { namespace Runtime {

class PE : public Module
{
    MOTOR_NOCOPY(PE);

private:
    struct StringTable
    {
        u32  size;
        char strings[1];
    };

private:
    SymbolResolver::SymbolInformations m_symbolInformations;

public:
    PE(const char* filename, u64 baseAddress);
    ~PE();

    operator void*() const
    {
        return 0;
    }
    bool operator!() const
    {
        return 0;
    }

    virtual Endianness endianness() const override
    {
        return Endianness_Little;
    }
    virtual SymbolResolver::SymbolInformations getSymbolInformation() const override;
};

}}  // namespace Motor::Runtime
