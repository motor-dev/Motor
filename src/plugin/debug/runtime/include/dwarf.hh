/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_DEBUG_RUNTIME_DWARF_HH_
#define MOTOR_DEBUG_RUNTIME_DWARF_HH_
/**************************************************************************************************/
#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/hashmap.hh>
#include <motor/plugin.debug.runtime/symbols.hh>
#include <elf.hh>

namespace Motor { namespace Runtime {

namespace Dwarf {
class CompilationUnit;
struct Abbreviation;
}  // namespace Dwarf

class DwarfModule : public SymbolResolver
{
    MOTOR_NOCOPY(DwarfModule);

private:
    class StringBuffer : public refcountable
    {
        MOTOR_NOCOPY(StringBuffer);

    private:
        const ref< const StringBuffer >  m_next;
        u64 const                        m_size;
        u64                              m_current;
        minitl::Allocator::Block< char > m_buffer;

    public:
        StringBuffer(size_t size, ref< const StringBuffer > next);
        ~StringBuffer();

        const char* store(const char* string, size_t size);
        char*       data();
    };

public:
    struct AddressRange
    {
        u64 begin;
        u64 end;

        static bool consistent(AddressRange range1, AddressRange range2);
        bool        operator<(AddressRange other) const;
        bool        operator==(AddressRange other) const;
    };

private:
    class CompilationUnit
    {
    public:
        const char*  name;
        AddressRange range;

        CompilationUnit() : name(0)
        {
        }
        ~CompilationUnit()
        {
        }
    };

private:
    template < Endianness e >
    class Buffer;
    typedef minitl::hashmap< AddressRange, CompilationUnit > UnitMap;

private:
    const u64           m_begin;
    const u64           m_end;
    const ifilename     m_moduleName;
    UnitMap             m_units;
    ref< StringBuffer > m_strings;
    char*               m_stringPool;

private:
    template < Endianness e >
    void parse(const Module& m);
    template < Endianness e >
    bool readInfos(Buffer< e >& buffer, UnitMap& units,
                   const minitl::vector< Dwarf::Abbreviation >& abbreviations, u8 ptrSize);
    template < Endianness e >
    bool fillNode(Buffer< e >& buffer, CompilationUnit& unit, const Dwarf::Abbreviation& abbrev,
                  const minitl::vector< Dwarf::Abbreviation >& abbreviations, u8 ptrSize);
    template < Endianness e >
    bool readAbbreviation(Buffer< e >&                           buffer,
                          minitl::vector< Dwarf::Abbreviation >& abbreviations);

public:
    DwarfModule(const ifilename& moduleName, const Module& m, u64 begin, u64 size);
    ~DwarfModule();

    virtual bool resolve(u64 address, Symbol& symbol) const override;

    const char* storeString(const char* string);
    const char* indexedString(u64 offset) const;
};

}}  // namespace Motor::Runtime

namespace minitl {

template <>
struct hash< Motor::Runtime::DwarfModule::AddressRange >
{
    bool operator()(const Motor::Runtime::DwarfModule::AddressRange& range1,
                    const Motor::Runtime::DwarfModule::AddressRange& range2)
    {
        return range1 == range2;
    }
    u32 operator()(const Motor::Runtime::DwarfModule::AddressRange& range)
    {
        return u32(range.begin ^ range.end);
    }
};

}  // namespace minitl
/**************************************************************************************************/
#endif
