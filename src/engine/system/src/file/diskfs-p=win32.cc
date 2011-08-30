/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <system/stdafx.h>
#include    <system/file/diskfs.hh>
#include    <core/memory/streams.hh>


namespace BugEngine
{

class MemoryFileMap : public IMemoryStream
{
private:
    HANDLE  m_file;
    HANDLE  m_fileMap;
    void*   m_pointer;
    i64     m_size;
    i64     m_offset;
public:
    MemoryFileMap(void* memory, size_t size, HANDLE file, HANDLE filemap);
    ~MemoryFileMap();
    
    virtual void*       basememory() override;
    virtual const void* basememory() const override;
    virtual i64         size() const override;
    virtual i64         offset() const override;
    virtual void        seek(SeekMethod method, i64 offset) override;
    virtual void        resize(i64 size) override;
    virtual bool        writable() const override;
};

MemoryFileMap::MemoryFileMap(void* memory, size_t size, HANDLE file, HANDLE filemap) :
    m_file(file),
    m_fileMap(filemap),
    m_pointer(memory),
    m_size(size),
    m_offset(0)
{
}

MemoryFileMap::~MemoryFileMap()
{
    UnmapViewOfFile(m_pointer);
    CloseHandle(m_fileMap);
    CloseHandle(m_file);
}

void* MemoryFileMap::basememory()
{
    return m_pointer;
}

const void* MemoryFileMap::basememory() const
{
    return m_pointer;
}

i64 MemoryFileMap::size() const
{
    return m_size;
}

i64 MemoryFileMap::offset() const
{
    return m_offset;
}

void MemoryFileMap::seek(SeekMethod method, i64 _offset)
{
    switch(method)
    {
        case eSeekMove:
            m_offset += _offset;
            break;
        case eSeekFromStart:
            m_offset = _offset;
            break;
        case eSeekFromEnd:
            m_offset = m_size + _offset;
            break;
        default:
            be_notreached();
    }
    if (m_offset < 0) m_offset = 0;
    if (m_offset > m_size) m_offset = m_size;
}

void MemoryFileMap::resize(i64 size)
{
    be_forceuse(size);
    be_notreached();
}

bool MemoryFileMap::writable() const
{
    return false;
}

//-----------------------------------------------------------------------------

DiskFS::DiskFS(const ipath& prefix, OpenMode mode)
    :   FileSystemComponent()
    ,   m_prefix(prefix)
    ,   m_readOnly(mode == ReadOnly)
{
    if (mode == CreateRoot)
    {
        CreateDirectoryA(prefix.str().c_str(), 0);
    }
}

DiskFS::~DiskFS(void)
{
}

bool DiskFS::writable() const
{
    return m_readOnly;
}

ref<IMemoryStream> DiskFS::open(const ifilename& filename, FileOpenMode mode) const
{
    minitl::format<ifilename::MaxFilenameLength> fullname = (m_prefix+filename).str();
    if (mode == eReadOnly)
    {
        HANDLE file = CreateFile(fullname.c_str(), GENERIC_READ, 0, 0, OPEN_EXISTING, 0, 0);
        if (file == INVALID_HANDLE_VALUE)
        {
            return ref<IMemoryStream>();
        }
        else
        {
            DWORD sizehigh;
            HANDLE filemap = CreateFileMapping(file, 0, PAGE_READONLY, 0, 0, 0);
            if (!filemap)
            {
                char *errorMessage = 0;
                int errorCode = ::GetLastError();
                FormatMessage( FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
                    NULL,
                    errorCode,
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                    reinterpret_cast<LPSTR>(&errorMessage),
                    0,
                    NULL);
                errorCode = ::GetLastError();
                be_error("%s : %s"|fullname|errorMessage);
                ::LocalFree(errorMessage);
                return ref<IMemoryStream>();
            }
            LPVOID memory = MapViewOfFile(filemap, FILE_MAP_READ, 0, 0, 0);
            if (!memory)
            {
                char *errorMessage = 0;
                int errorCode = ::GetLastError();
                FormatMessage( FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
                    NULL,
                    errorCode,
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                    reinterpret_cast<LPSTR>(&errorMessage),
                    0,
                    NULL);
                errorCode = ::GetLastError();
                be_error("%s : %s"|fullname|errorMessage);
                ::LocalFree(errorMessage);
                return ref<IMemoryStream>();
            }
            return ref<MemoryFileMap>::create(gameArena(), memory, GetFileSize(file, &sizehigh), file, filemap);
        }
    }
    else
        return ref<IMemoryStream>();
}

size_t DiskFS::age(const ifilename& file) const
{
    minitl::format<ifilename::MaxFilenameLength> fullname = (m_prefix+file).str();
    return 0;
}

}