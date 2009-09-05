/*****************************************************************************\
* BugEngine                                                                   *
* Copyright (C) 2005-2008  screetch <screetch@gmail.com>                      *
*                                                                             *
* This library is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This library is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public        *
* License for more details.                                                   *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this library; if not, write to                                   *
* the Free Software Foundation, Inc.,                                         *
* 51 Franklin St,                                                             *
* Fifth Floor,                                                                *
* Boston, MA                                                                  *
* 02110-1301  USA                                                             *
\*****************************************************************************/

#include    <core/stdafx.h>
#include    <core/memory/streams.hh>

namespace BugEngine
{

AbstractMemoryStream::AbstractMemoryStream()
{
}

AbstractMemoryStream::~AbstractMemoryStream()
{
}

void* AbstractMemoryStream::memory()
{
    return static_cast<void*>(static_cast<char*>(basememory())+offset());
}

i64 AbstractMemoryStream::read(void* buffer, i64 _size)
{
    i64 toread = std::min(_size,size()-offset());
    memcpy(buffer, memory(), checked_numcast<size_t>(toread));
    seek(eSeekMove, toread);
    return toread;
}

void AbstractMemoryStream::write(void* buffer, i64 _size)
{
    be_assert(writable(), "writing in a read-only memory stream");
    if(_size > size()-offset())
        resize(offset()+_size);
    memcpy(memory(),buffer,checked_numcast<size_t>(_size));
    seek(eSeekMove, _size);
}

/*****************************************************************************/

MemoryStream::MemoryStream() :
    m_memory(0),
    m_size(0),
    m_offset(0)
{
}

MemoryStream::MemoryStream(i64 _size) :
    m_memory(be_malloc(checked_numcast<size_t>(_size))),
    m_size(_size),
    m_offset(0)
{
}

MemoryStream::~MemoryStream()
{
    be_free(m_memory);
}

void* MemoryStream::basememory()
{
    return m_memory;
}

i64 MemoryStream::size() const
{
    return m_size;
}

i64 MemoryStream::offset() const
{
    return m_offset;
}

void MemoryStream::seek(SeekMethod method, i64 _offset)
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
    if(m_offset < 0) m_offset = 0;
    if(m_offset > m_size) m_offset = m_size;
}

void MemoryStream::resize(i64 _size)
{
    void* buffer = realloc(m_memory,checked_numcast<size_t>(_size));
    if(! buffer)
        throw std::bad_alloc();
    m_memory = buffer;
    m_size = _size;
    if(m_offset > m_size) m_offset = m_size;
}

bool MemoryStream::writable() const
{
    return true;
}

//-----------------------------------------------------------------------------


}
