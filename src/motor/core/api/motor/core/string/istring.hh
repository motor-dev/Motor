/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_STRING_ISTRING_HH
#define MOTOR_CORE_STRING_ISTRING_HH

#include <motor/core/coredefs.hh>
#include <motor/minitl/format.hh>

namespace Motor {

class motor_api(CORE) istring
{
private:
    u32 m_index;

private:
    static u32 init(const char* str);
    static u32 init(const char* begin, const char* end);

public:
    istring();
    explicit istring(const char* value);
    template < u32 BUFFER_SIZE >
    explicit istring(const minitl::format_buffer< BUFFER_SIZE >& str) : m_index(init(str.buffer))
    {
    }
    istring(const char* begin, const char* end);
    istring(istring && other) noexcept = default;
    istring(const istring& other)      = default;

    ~istring() = default;

    istring& operator=(const istring& other)     = default;
    istring& operator=(istring&& other) noexcept = default;

    const char* c_str() const;
    u32         size() const;
    u32         hash() const;

    bool operator==(const istring& other) const;
    bool operator!=(const istring& other) const;
    bool operator<(const istring& other) const;
};

class motor_api(CORE) igenericnamespace
{
private:
    static constexpr u32 MaxNamespaceSize = 8;

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
    static constexpr char Separator     = '.';
    static constexpr u32  MaxPathLength = 1024;

    struct Path
    {
        char name[MaxPathLength];
        operator const char*() const  // NOLINT(google-explicit-constructor)
        {
            return name;
        }
    };
    inamespace();
    explicit inamespace(const istring& onlycomponent);
    explicit inamespace(const char* str);
    ~inamespace() = default;
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
    static constexpr char Separator         = '/';
    static constexpr u32  MaxFilenameLength = 1024;

    struct Filename
    {
        char name[MaxFilenameLength];

        operator const char*() const  // NOLINT(google-explicit-constructor)
        {
            return name;
        }
    };
    ifilename();
    explicit ifilename(const istring& onlycomponent);
    explicit ifilename(const char* str);
    explicit ifilename(const ipath& path);
    ~ifilename() = default;

    Filename str(char separator = Separator) const;
};

class motor_api(CORE) ipath : public igenericnamespace
{
public:
    static constexpr char Separator         = '/';
    static constexpr u32  MaxFilenameLength = 1024;

    struct Filename
    {
        char name[MaxFilenameLength];

        operator const char*() const  // NOLINT(google-explicit-constructor)
        {
            return name;
        }
    };
    ipath();
    explicit ipath(const istring& onlycomponent);
    explicit ipath(const char* str);
    ipath(const char* begin, const char* end);
    ~ipath() = default;

    ipath&   operator+=(const ipath& other);
    Filename str(char separator = Separator) const;
};

motor_api(CORE) ipath     operator+(const ipath& path1, const ipath& path2);
motor_api(CORE) ifilename operator+(const ipath& path, const ifilename& file);

motor_api(CORE) u32 format_length(const istring& s, const minitl::format_options& options);
motor_api(CORE) u32 format_arg(char* destination, const istring& value,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(CORE) u32
    format_arg_partial(char* destination, const istring& value,
                       const minitl::format_options& options, u32 reservedLength, u32 maxCapacity);

motor_api(CORE) u32
    format_length(const igenericnamespace& n, const minitl::format_options& options);
motor_api(CORE) u32 format_arg(char* destination, const inamespace& value,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(CORE) u32 format_arg(char* destination, const ipath& value,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(CORE) u32
    format_arg_partial(char* destination, const inamespace& value,
                       const minitl::format_options& options, u32 reservedLength, u32 maxCapacity);
motor_api(CORE) u32
    format_arg_partial(char* destination, const ipath& value, const minitl::format_options& options,
                       u32 reservedLength, u32 maxCapacity);
motor_api(CORE) u32 format_arg(char* destination, const ifilename& value,
                               const minitl::format_options& options, u32 reservedLength);
motor_api(CORE) u32
    format_arg_partial(char* destination, const ifilename& value,
                       const minitl::format_options& options, u32 reservedLength, u32 maxCapacity);

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

}  // namespace minitl

#endif
