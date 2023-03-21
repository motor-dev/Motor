/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_CORE_STRING_ISTRING_HH_
#define MOTOR_CORE_STRING_ISTRING_HH_
/**************************************************************************************************/
#include <motor/core/stdafx.h>
#include <motor/minitl/format.hh>

namespace Motor {

class motor_api(CORE) istring
{
private:
    u32 m_index;

private:
    u32 init(const char* str);
    u32 init(const char* begin, const char* end);

public:
    istring();
    istring(const char* str);
    template < u32 BUFFER_SIZE >
    istring(const minitl::format_buffer< BUFFER_SIZE >& str) : m_index(init(str.buffer))
    {
    }
    istring(const char* begin, const char* end);
    istring(istring && other);
    istring(const istring& other);

    ~istring();

    istring& operator=(const istring& other);
    istring& operator=(istring&& other);

    const char* c_str() const;
    size_t      size() const;
    u32         hash() const;

    bool operator==(const istring& other) const;
    bool operator!=(const istring& other) const;
    bool operator<(const istring& other) const;
};

class motor_api(CORE) igenericnamespace
{
private:
    enum Constants
    {
        MaxNamespaceSize = 8
    };

private:
    istring* m_namespace;
    char     m_buffer[sizeof(istring) * MaxNamespaceSize];
    u16      m_size;
    u16      m_capacity;

private:
    void grow(u16 newCapacity);

protected:
    igenericnamespace();
    explicit igenericnamespace(const istring& onlycomponent);
    igenericnamespace(const igenericnamespace& other);
    igenericnamespace(const char* str, const char* sep);
    igenericnamespace(const char* begin, const char* end, const char* sep);
    ~igenericnamespace();
    igenericnamespace& operator=(const igenericnamespace& other);
    void               str(char* buffer, char separator, u32 size) const;

public:
    u32            size() const;
    const istring& operator[](u32 index) const;

    void    push_back(const istring& component);
    istring pop_back();
    istring pop_front();

    bool operator==(const igenericnamespace& other) const;
    bool operator!=(const igenericnamespace& other) const;
};

motor_api(CORE) bool startswith(const igenericnamespace& start, const igenericnamespace& full);
motor_api(CORE) bool operator<(const igenericnamespace& ns1, const igenericnamespace& ns2);

class motor_api(CORE) inamespace : public igenericnamespace
{
public:
    enum
    {
        Separator     = '.',
        MaxPathLength = 1024
    };
    struct Path
    {
        char name[MaxPathLength];
             operator const char*() const
        {
            return name;
        }
    };
    inamespace();
    explicit inamespace(const istring& onlycomponent);
    inamespace(const char* str);
    ~inamespace()
    {
    }
    inamespace& operator+=(const inamespace& other);
    inamespace& operator+=(const istring& component);

    Path str(char separator = Separator) const;
};

motor_api(CORE) inamespace operator+(const istring& str1, const istring& str2);
motor_api(CORE) inamespace operator+(const istring& str1, const inamespace& ns2);
motor_api(CORE) inamespace operator+(const inamespace& ns1, const istring& str2);
motor_api(CORE) inamespace operator+(const inamespace& ns1, const inamespace& ns2);

class ipath;

class motor_api(CORE) ifilename : public igenericnamespace
{
public:
    enum
    {
        Separator         = '/',
        MaxFilenameLength = 1024
    };
    struct Filename
    {
        char name[MaxFilenameLength];

        operator const char*() const
        {
            return name;
        }
    };
    ifilename();
    explicit ifilename(const istring& onlycomponent);
    explicit ifilename(const char* str);
    explicit ifilename(const ipath& path);
    ~ifilename()
    {
    }

    Filename str(char separator = Separator) const;
};

class motor_api(CORE) ipath : public igenericnamespace
{
public:
    enum
    {
        Separator         = '/',
        MaxFilenameLength = 1024
    };
    struct Filename
    {
        char name[MaxFilenameLength];

        operator const char*() const
        {
            return name;
        }
    };
    ipath();
    explicit ipath(const istring& onlycomponent);
    explicit ipath(const char* str);
    ipath(const char* begin, const char* end);
    ~ipath()
    {
    }

    ipath&   operator+=(const ipath& other);
    Filename str(char separator = Separator) const;
};

motor_api(CORE) ipath     operator+(const ipath& path1, const ipath& path2);
motor_api(CORE) ifilename operator+(const ipath& path, const ifilename& file);

}  // namespace Motor

#include <motor/minitl/hash.hh>

namespace minitl {

template <>
struct hash< Motor::istring >
{
    inline u32 operator()(const Motor::istring& v)
    {
        return v.hash();
    }
    inline int operator()(const Motor::istring& v1, const Motor::istring& v2)
    {
        return v1 == v2;
    }
};

template <>
struct formatter< Motor::istring > : public formatter< const char* >
{
    static u32 length(const Motor::istring& value, const format_options& options)
    {
        motor_forceuse(options);
        return value.size();
    }
    static u32 format_to_partial(char* destination, const Motor::istring& value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        return formatter< const char* >::format_to_partial(destination, value.c_str(), options,
                                                           reservedLength, maximalLength);
    }
    static u32 format_to(char* destination, const Motor::istring& value,
                         const format_options& options, u32 reservedLength)
    {
        return formatter< const char* >::format_to(destination, value.c_str(), options,
                                                   reservedLength);
    }
};

template <>
struct formatter< Motor::inamespace > : public formatter< const char* >
{
    static u32 length(const Motor::inamespace& value, const format_options& options)
    {
        motor_forceuse(options);
        u32 result = 0;

        if(value.size())
        {
            result += value[0].size();
            for(u32 i = 1; i < value.size(); ++i)
            {
                result += 1 + value[i].size();
            }
        }
        return result;
    }
    static u32 format_to_partial(char* destination, const Motor::inamespace& value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        return formatter< const char* >::format_to_partial(destination, value.str(), options,
                                                           reservedLength, maximalLength);
    }
    static u32 format_to(char* destination, const Motor::inamespace& value,
                         const format_options& options, u32 reservedLength)
    {
        return formatter< const char* >::format_to(destination, value.str(), options,
                                                   reservedLength);
    }
};

template <>
struct formatter< Motor::ifilename > : public formatter< const char* >
{
    static u32 length(const Motor::ifilename& value, const format_options& options)
    {
        motor_forceuse(options);
        u32 result = 0;

        if(value.size())
        {
            result += value[0].size();
            for(u32 i = 1; i < value.size(); ++i)
            {
                result += 1 + value[i].size();
            }
        }
        return result;
    }
    static u32 format_to_partial(char* destination, const Motor::ifilename& value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        return formatter< const char* >::format_to_partial(destination, value.str(), options,
                                                           reservedLength, maximalLength);
    }
    static u32 format_to(char* destination, const Motor::ifilename& value,
                         const format_options& options, u32 reservedLength)
    {
        return formatter< const char* >::format_to(destination, value.str(), options,
                                                   reservedLength);
    }
};

template <>
struct formatter< Motor::ipath > : public formatter< const char* >
{
    static u32 length(const Motor::ipath& value, const format_options& options)
    {
        motor_forceuse(options);
        u32 result = 0;

        if(value.size())
        {
            result += value[0].size();
            for(u32 i = 1; i < value.size(); ++i)
            {
                result += 1 + value[i].size();
            }
        }
        return result;
    }
    static u32 format_to_partial(char* destination, const Motor::ipath& value,
                                 const format_options& options, u32 reservedLength,
                                 u32 maximalLength)
    {
        return formatter< const char* >::format_to_partial(destination, value.str(), options,
                                                           reservedLength, maximalLength);
    }
    static u32 format_to(char* destination, const Motor::ipath& value,
                         const format_options& options, u32 reservedLength)
    {
        return formatter< const char* >::format_to(destination, value.str(), options,
                                                   reservedLength);
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
