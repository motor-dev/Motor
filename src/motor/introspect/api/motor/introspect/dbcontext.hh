/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_INTROSPECT_DBCONTEXT_HH
#define MOTOR_INTROSPECT_DBCONTEXT_HH

#include <motor/introspect/stdafx.h>
#include <motor/filesystem/folder.meta.hh>
#include <motor/introspect/dbnamespace.hh>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta { namespace AST {

struct Message
{
    typedef minitl::format_buffer< 512u > MessageType;
    weak< const Node >                    owner;
    MessageType                           message;
    LogLevel                              severity;
    Message(const weak< const Node >& owner, const MessageType& message, LogLevel severity)
        : owner(owner)
        , message(message)
        , severity(severity)
    {
    }
};
typedef minitl::vector< Message > MessageList;

struct motor_api(INTROSPECT) DbContext
{
    ref< Namespace > const rootNamespace;
    ref< Folder > const    rootFolder;
    MessageList            messages;
    u32                    errorCount;

    DbContext(minitl::allocator & arena, const ref< Folder >& rootFolder);
    DbContext(minitl::allocator & arena, const ref< Namespace >& ns,
              const ref< Folder >& rootFolder);
    void error(const weak< const Node >& owner, const Message::MessageType& error);
    void warning(const weak< const Node >& owner, const Message::MessageType& warning);
    void info(const weak< const Node >& owner, const Message::MessageType& info);
};

}}}  // namespace Motor::Meta::AST

#endif
