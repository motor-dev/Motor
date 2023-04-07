/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

namespace minitl {

template < u32 BITS >
bitset< BITS >::bitset()
{
    for(u32 i = 0; i < (u32)Bytes; ++i)
    {
        m_bytes[i] = 0;
    }
}

template < u32 BITS >
typename bitset< BITS >::bit bitset< BITS >::operator[](u32 index)
{
    motor_assert_format(index < BITS, "bit index {0} out of range (size: {1})", index, BITS);
    bit result(*this, index);
    return result;
}

template < u32 BITS >
bool bitset< BITS >::operator[](u32 index) const
{
    motor_assert_format(index < BITS, "bit index {0} out of range (size: {1})", index, BITS);
    return 1 & (m_bytes[index / 8] >> (index % 8));
}

template < u32 BITS >
bitset< BITS >& bitset< BITS >::operator&=(const bitset< BITS >& rhs)
{
    for(u32 i = 0; i < (u32)Bytes; ++i)
    {
        m_bytes[i] &= rhs.m_bytes[i];
    }
    return *this;
}

template < u32 BITS >
bitset< BITS >& bitset< BITS >::operator|=(const bitset< BITS >& rhs)
{
    for(u32 i = 0; i < (u32)Bytes; ++i)
    {
        m_bytes[i] |= rhs.m_bytes[i];
    }
    return *this;
}

template < u32 BITS >
bitset< BITS >& bitset< BITS >::operator^=(const bitset< BITS >& rhs)
{
    for(u32 i = 0; i < (u32)Bytes; ++i)
    {
        m_bytes[i] ^= rhs.m_bytes[i];
    }
    return *this;
}

template < u32 BITS >
bitset< BITS > bitset< BITS >::operator~() const
{
    bitset< BITS > result;
    for(u32 i = 0; i < (u32)Bytes; ++i)
    {
        result.m_bytes[i] = ~m_bytes[i];
    }
    return result;
}

template < u32 BITS >
bool bitset< BITS >::operator==(const bitset< BITS >& rhs) const
{
    bool result = true;
    for(u32 i = 0; i < (u32)Bytes - 1; ++i)
    {
        result &= (m_bytes[i] == rhs.m_bytes[i]);
    }
    result &= ((m_bytes[Bytes - 1] & ((1 << BITS % 8) - 1))
               == (rhs.m_bytes[Bytes - 1] & ((1 << BITS % 8) - 1)));
    return result;
}

template < u32 BITS >
bool bitset< BITS >::operator!=(const bitset< BITS >& rhs) const
{
    bool result = true;
    for(u32 i = 0; i < (u32)Bytes - 1; ++i)
    {
        result &= (m_bytes[i] != rhs.m_bytes[i]);
    }
    result &= ((m_bytes[Bytes - 1] & ((1 << BITS % 8) - 1)) != (rhs.m_bytes[Bytes - 1])
               & ((1 << BITS % 8) - 1));
    return result;
}

template < u32 BITS >
bitset< BITS >::bit::operator bool() const
{
    return 1 & (owner.m_bytes[index / 32] >> (index % 32));
}

template < u32 BITS >
typename bitset< BITS >::bit& bitset< BITS >::bit::operator=(bool value)
{
    if(value)
    {
        owner.m_bytes[index / 8] |= (1u << (index % 8));
    }
    else
    {
        owner.m_bytes[index / 8] &= ~(1u << (index % 8));
    }
    return *this;
}

template < u32 BITS >
u32 bitset< BITS >::operator()(u32 begin, u32 end) const
{
    motor_assert(end - begin < 32, "too many bits to unpack for subset");
    u32       offset = begin % 8;
    const u8* bytes  = &m_bytes[begin / 8];
    u32 result = bytes[0] >> offset | u32(bytes[1]) << (8 - offset) | u32(bytes[2]) << (16 - offset)
                 | u32(bytes[3]) << (24 - offset) | u32(bytes[4]) << (32 - offset);
    u32 mask = 1 << (end - begin);
    mask |= mask << 1;
    mask |= mask << 2;
    mask |= mask << 4;
    mask |= mask << 8;
    mask |= mask << 16;
    mask = ~mask;
    return result & mask;
}

}  // namespace minitl
