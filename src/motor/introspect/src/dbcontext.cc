/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <motor/introspect/dbcontext.hh>

namespace Motor { namespace Meta { namespace AST {

DbContext::DbContext(minitl::Allocator& arena, const ref< Folder >& rootFolder)
    : rootNamespace(ref< Namespace >::create(arena, byref(arena)))
    , rootFolder(rootFolder)
    , messages(arena)
    , errorCount()
{
}

DbContext::DbContext(minitl::Allocator& arena, const ref< Namespace >& ns,
                     const ref< Folder >& rootFolder)
    : rootNamespace(ns)
    , rootFolder(rootFolder)
    , messages(arena)
    , errorCount()
{
}

void DbContext::error(const weak< const Node >& owner, const Message::MessageType& error)
{
    messages.emplace_back(owner, error, logError);
    errorCount++;
}

void DbContext::warning(const weak< const Node >& owner, const Message::MessageType& warning)
{
    messages.emplace_back(owner, warning, logWarning);
}

void DbContext::info(const weak< const Node >& owner, const Message::MessageType& info)
{
    messages.emplace_back(owner, info, logInfo);
}

}}}  // namespace Motor::Meta::AST
